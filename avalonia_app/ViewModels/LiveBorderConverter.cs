using System.Globalization;
using Avalonia.Data.Converters;
using Avalonia.Media;

namespace NakhonPartsDashboard.ViewModels;

public class LiveBorderConverter : IValueConverter
{
    public static readonly LiveBorderConverter Instance = new();

    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        bool isLive = value is bool b && b;
        return isLive
            ? new SolidColorBrush(Color.Parse("#22C55E"))
            : new SolidColorBrush(Color.Parse("#2A3345"));
    }

    public object ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
