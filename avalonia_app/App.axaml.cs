using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using NakhonPartsDashboard.ViewModels;
using NakhonPartsDashboard.Views;
using SkiaSharp;

namespace NakhonPartsDashboard;

public partial class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);

        // Register global typeface for LiveCharts to display Thai characters correctly in legends and tooltips
        LiveCharts.Configure(config =>
            config.HasGlobalSKTypeface(SKTypeface.FromFamilyName("Tahoma"))
        );
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            desktop.MainWindow = new MainWindow
            {
                DataContext = new MainWindowViewModel()
            };
        }
        base.OnFrameworkInitializationCompleted();
    }
}
