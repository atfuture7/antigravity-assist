using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace MyHelloWorldApp;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }
// 4. Logic to append text when button is clicked
    private void OnAppendClick(object sender, RoutedEventArgs e)
    {
        if (!string.IsNullOrWhiteSpace(InputSlot.Text))
        {
            // Append text to existing label
            DisplayLabel.Text += " " + InputSlot.Text;
            
            // Clear the input
            InputSlot.Clear();
        }
    }
}