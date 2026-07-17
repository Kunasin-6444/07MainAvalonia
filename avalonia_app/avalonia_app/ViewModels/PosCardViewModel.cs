using CommunityToolkit.Mvvm.ComponentModel;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using NakhonPartsDashboard.Models;
using SkiaSharp;

namespace NakhonPartsDashboard.ViewModels;

public partial class PosCardViewModel : ObservableObject
{
    public string SaleLot { get; }
    public string PosLabel => $"POS {SaleLot}";
    public double LastSaleTotal { get; }
    public double Credit { get; }
    public double Transfer { get; }
    public double Cash { get; }
    public bool IsLive { get; }

    public ISeries[] TrendSeries { get; }

    public PosCardViewModel(PosStatusModel model)
    {
        SaleLot = model.SaleLot;
        LastSaleTotal = model.LastSaleTotal;
        Credit = model.Credit;
        Transfer = model.Transfer;
        Cash = model.Cash;
        IsLive = model.IsLive;

        var lineColor = IsLive ? SKColors.LimeGreen : SKColors.DodgerBlue;

        TrendSeries = new ISeries[]
        {
            new LineSeries<double>
            {
                Values = model.Trend,
                Fill = null,
                GeometrySize = 0,
                LineSmoothness = 0.6,
                Stroke = new LiveChartsCore.SkiaSharpView.Painting.SolidColorPaint(lineColor, 2)
            }
        };
    }
}
