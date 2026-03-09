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

namespace _260308_cs_input_window;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

    private void SubmitButton_Click(object sender, RoutedEventArgs e)
    {
        ResultTextBlock.Text = $"Showing input: {ShowingInputTextBox.Text}\nhidden input: {HiddenInputTextBox.Password}";
        ShowingInputTextBox.Clear();
        HiddenInputTextBox.Clear();
    }
}