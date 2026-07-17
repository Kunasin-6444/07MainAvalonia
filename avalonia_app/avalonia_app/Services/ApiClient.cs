using System.Net.Http.Json;
using NakhonPartsDashboard.Models;

namespace NakhonPartsDashboard.Services;

public class ApiClient
{
    private readonly HttpClient _http;

    // BaseAddress MUST end with '/' — if it doesn't, HttpClient drops the port
    // when a relative path starts with '/', causing requests to hit the wrong URL.
    private const string BaseUrl = "http://127.0.0.1:8000/";

    public ApiClient()
    {
        _http = new HttpClient
        {
            BaseAddress = new Uri(BaseUrl),
            // 15 s timeout — queries now take ~5s with DB indexes in place.
            Timeout = TimeSpan.FromSeconds(15)
        };
    }

    public async Task<List<PosStatusModel>> GetPosStatusAsync()
    {
        // Relative path must NOT start with '/' when BaseAddress ends with '/'
        var result = await _http.GetFromJsonAsync<List<PosStatusModel>>("pos/status");
        return result ?? new List<PosStatusModel>();
    }

    public async Task<TransactionsResponse> GetLatestTransactionsAsync()
    {
        var result = await _http.GetFromJsonAsync<TransactionsResponse>("pos/latest-transactions");
        return result ?? new TransactionsResponse();
    }
}
