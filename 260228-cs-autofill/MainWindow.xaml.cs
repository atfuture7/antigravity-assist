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

using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

// Define an alias to resolve the conflict
using WinForms = System.Windows.Forms;

namespace autofill;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }

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

    private void OnClearClick(object sender, RoutedEventArgs e)
    {
        DisplayLabel.Text = string.Empty;

    }

    private async void OnSendToAppClick(object sender, RoutedEventArgs e)
    {
        string textToSend = DisplayLabel.Text;

        // 1. Give the user 3 seconds to click on the target app (Notepad, Browser, etc.)
        DisplayLabel.Text = "Click the target app now! (3s remaining...)";
        await Task.Delay(3000);

        // 2. Clear the target input first
        // ^a = Ctrl + A (Select All)
        // {BACKSPACE} = Delete the selection
        WinForms.SendKeys.SendWait("^a{BACKSPACE}");

        // 3. Use SendKeys to "type" the text into whatever window is focused
        // Note: We use System.Windows.Forms for SendWait
        WinForms.SendKeys.SendWait(textToSend);

        // 4. Reset the label
        DisplayLabel.Text = textToSend;
    }
}