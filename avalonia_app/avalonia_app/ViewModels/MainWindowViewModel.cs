using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Windows.Input;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using NakhonPartsDashboard.Models;
using NakhonPartsDashboard.Services;
using SkiaSharp;

namespace NakhonPartsDashboard.ViewModels;

/// <summary>
/// Main view-model — does NOT use [ObservableProperty] / [RelayCommand] source
/// generators to avoid the duplicate-analyzer bug in .NET SDK 10 with
/// CommunityToolkit.Mvvm.  Plain INotifyPropertyChanged is used instead.
/// </summary>
public class MainWindowViewModel : INotifyPropertyChanged
{

    private readonly ApiClient _api = new();
    private readonly System.Timers.Timer _refreshTimer;

    // ── INotifyPropertyChanged ───────────────────────────────────────────────
    public event PropertyChangedEventHandler? PropertyChanged;
    private void OnPropertyChanged([CallerMemberName] string? name = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));

    // ── Observable properties ─────────────────────────────────────────────────
    private ObservableCollection<PosCardViewModel> _posCards = new();
    public ObservableCollection<PosCardViewModel> PosCards
    {
        get => _posCards;
        set { _posCards = value; OnPropertyChanged(); }
    }

    private ObservableCollection<TransactionModel> _transactions = new();
    public ObservableCollection<TransactionModel> Transactions
    {
        get => _transactions;
        set { _transactions = value; OnPropertyChanged(); }
    }

    private ISeries[] _donutSeries = Array.Empty<ISeries>();
    public ISeries[] DonutSeries
    {
        get => _donutSeries;
        set { _donutSeries = value; OnPropertyChanged(); }
    }

    private string _statusMessage = "Loading...";
    public string StatusMessage
    {
        get => _statusMessage;
        set { _statusMessage = value; OnPropertyChanged(); }
    }

    // ADD THIS for the legend text color
    private LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint _legendTextPaint = 
        new(SKColors.White);
    public LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint LegendTextPaint
    {
        get => _legendTextPaint;
        set { _legendTextPaint = value; OnPropertyChanged(); }
    }

    // ── Command ───────────────────────────────────────────────────────────────
    public ICommand LoadDataCommand { get; }

    public MainWindowViewModel()
    {
        LoadDataCommand = new AsyncRelayCommand(LoadDataAsync);

        _refreshTimer = new System.Timers.Timer(15_000); // refresh every 15 s
        _refreshTimer.Elapsed += async (_, _) => await LoadDataAsync();
        _refreshTimer.Start();

        _ = LoadDataAsync();
    }

    private volatile bool _isLoading = false;

    private async Task LoadDataAsync()
    {
        if (_isLoading) return;
        _isLoading = true;

        try
        {
            // Single round-trip to /pos/dashboard — server runs the heavy JOIN
            // query exactly once and returns all data. Eliminates MySQL I/O
            // contention that caused timeouts when two parallel queries ran.
            var dashboard = await _api.GetDashboardAsync();

            await Avalonia.Threading.Dispatcher.UIThread.InvokeAsync(() =>
            {
                PosCards = new ObservableCollection<PosCardViewModel>(
                    dashboard.PosCards.Select(s => new PosCardViewModel(s)));

                Transactions = new ObservableCollection<TransactionModel>(dashboard.Transactions);

                DonutSeries = BuildDonutSeries(dashboard.PaymentSummary);
                StatusMessage = $"Updated {DateTime.Now:HH:mm:ss}";
            });
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[LoadDataAsync ERROR] {ex.GetType().Name}: {ex.Message}");
            Console.WriteLine(ex.ToString());
            StatusMessage = $"Error: {ex.GetType().Name} — {ex.Message}";
        }
        finally
        {
            _isLoading = false;
        }
    }

    private static ISeries[] BuildDonutSeries(PaymentSummary summary)
    {
        return new ISeries[]
        {
            new PieSeries<double>
            {
                Values = new[] { summary.Credit.BillCount * 1.0 },
                Name = "เครดิต",
                InnerRadius = 50,
                Fill = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(SKColors.DodgerBlue),
                ToolTipLabelFormatter = _ =>
                    $"เครดิต: {summary.Credit.Percent}% ({summary.Credit.TotalAmount:N0} บาท)"
            },
            new PieSeries<double>
            {
                Values = new[] { summary.Transfer.BillCount * 1.0 },
                Name = "โอนเงิน",
                InnerRadius = 50,
                Fill = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(SKColors.LimeGreen),
                ToolTipLabelFormatter = _ =>
                    $"โอนเงิน: {summary.Transfer.Percent}% ({summary.Transfer.TotalAmount:N0} บาท)"
            },
            new PieSeries<double>
            {
                Values = new[] { summary.Cash.BillCount * 1.0 },
                Name = "เงินสด",
                InnerRadius = 50,
                Fill = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(SKColors.OrangeRed),
                ToolTipLabelFormatter = _ =>
                    $"เงินสด: {summary.Cash.Percent}% ({summary.Cash.TotalAmount:N0} บาท)"
            }
        };
    }
}

/// <summary>Minimal ICommand wrapper for async tasks.</summary>
public class AsyncRelayCommand : ICommand
{
    private readonly Func<Task> _execute;
    private bool _isExecuting;

    public AsyncRelayCommand(Func<Task> execute) => _execute = execute;

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => !_isExecuting;

    public async void Execute(object? parameter)
    {
        if (_isExecuting) return;
        _isExecuting = true;
        CanExecuteChanged?.Invoke(this, EventArgs.Empty);
        try   { await _execute(); }
        finally
        {
            _isExecuting = false;
            CanExecuteChanged?.Invoke(this, EventArgs.Empty);
        }
    }
}
