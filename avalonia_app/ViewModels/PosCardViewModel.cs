using CommunityToolkit.Mvvm.ComponentModel;
using NakhonPartsDashboard.Models;

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

    public PosCardViewModel(PosStatusModel model)
    {
        SaleLot = model.SaleLot;
        LastSaleTotal = model.LastSaleTotal;
        Credit = model.Credit;
        Transfer = model.Transfer;
        Cash = model.Cash;
        IsLive = model.IsLive;
    }
}
