using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using NakhonPartsDashboard.Models;
using NakhonPartsDashboard.Services;
using SkiaSharp;

namespace NakhonPartsDashboard.ViewModels;

public partial class MainWindowViewModel : ObservableObject
{
    private readonly ApiClient _api = new();
    private readonly System.Timers.Timer _refreshTimer;

    [ObservableProperty]
    private ObservableCollection<PosCardViewModel> _posCards = new();

    [ObservableProperty]
    private ObservableCollection<TransactionModel> _transactions = new();

    [ObservableProperty]
    private ISeries[] _donutSeries = Array.Empty<ISeries>();

    [ObservableProperty]
    private string _statusMessage = "Loading...";

    public MainWindowViewModel()
    {
        _refreshTimer = new System.Timers.Timer(15_000); // refresh every 15s (queries now ~5s with DB indexes)
        _refreshTimer.Elapsed += async (_, _) => await LoadDataAsync();
        _refreshTimer.Start();

        _ = LoadDataAsync();
    }

    private volatile bool _isLoading = false;

    [RelayCommand]
    private async Task LoadDataAsync()
    {
        // Prevent concurrent calls: if a load is already in progress (e.g. from
        // the timer firing while the previous request is still running), skip it.
        if (_isLoading) return;
        _isLoading = true;

        try
        {
            // Run both API calls in parallel — cuts total wait from
            // (posStatus + transactions) sequential to max(posStatus, transactions).
            var posTask = _api.GetPosStatusAsync();
            var txTask  = _api.GetLatestTransactionsAsync();
            await Task.WhenAll(posTask, txTask);

            var statusList = posTask.Result;
            var txResponse = txTask.Result;

            // Must update ObservableCollections on the UI thread
            await Avalonia.Threading.Dispatcher.UIThread.InvokeAsync(() =>
            {
                PosCards = new ObservableCollection<PosCardViewModel>(
                    statusList.Select(s => new PosCardViewModel(s)));

                Transactions = new ObservableCollection<TransactionModel>(txResponse.Transactions);

                DonutSeries = BuildDonutSeries(txResponse.PaymentSummary);
                StatusMessage = $"Updated {DateTime.Now:HH:mm:ss}";
            });
        }
        catch (Exception ex)
        {
            // Print full details to console so the real cause is visible
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
                Fill = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(SKColors.DodgerBlue),
                ToolTipLabelFormatter = _ =>
                    $"เครดิต: {summary.Credit.Percent}% ({summary.Credit.TotalAmount:N0} บาท)"
            },
            new PieSeries<double>
            {
                Values = new[] { summary.Transfer.BillCount * 1.0 },
                Name = "โอนเงิน",
                Fill = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(SKColors.LimeGreen),
                ToolTipLabelFormatter = _ =>
                    $"โอนเงิน: {summary.Transfer.Percent}% ({summary.Transfer.TotalAmount:N0} บาท)"
            },
            new PieSeries<double>
            {
                Values = new[] { summary.Cash.BillCount * 1.0 },
                Name = "เงินสด",
                Fill = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(SKColors.OrangeRed),
                ToolTipLabelFormatter = _ =>
                    $"เงินสด: {summary.Cash.Percent}% ({summary.Cash.TotalAmount:N0} บาท)"
            }
        };
    }
}
