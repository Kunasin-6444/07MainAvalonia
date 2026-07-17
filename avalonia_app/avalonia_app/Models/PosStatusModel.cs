using System.Text.Json.Serialization;

namespace NakhonPartsDashboard.Models;

public class PosStatusModel
{
    [JsonPropertyName("sale_lot")]
    public string SaleLot { get; set; } = "";

    [JsonPropertyName("last_sale_total")]
    public double LastSaleTotal { get; set; }

    [JsonPropertyName("credit")]
    public double Credit { get; set; }

    [JsonPropertyName("transfer")]
    public double Transfer { get; set; }

    [JsonPropertyName("cash")]
    public double Cash { get; set; }

    [JsonPropertyName("trend")]
    public List<double> Trend { get; set; } = new();

    [JsonPropertyName("is_live")]
    public bool IsLive { get; set; }
}
