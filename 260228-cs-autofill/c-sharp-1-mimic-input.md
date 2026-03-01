# C# Mimic INPUT



## Frame work

VS Code doesn't have a "File > New WPF Project" button like the big Visual Studio, so we use the **.NET CLI**. Open your terminal in VS Code and run:

```bash
# Create a new WPF project
dotnet new wpf -n MyHelloWorldApp

# Move into the folder
cd MyHelloWorldApp

```

This command generates the following structure automatically:

* **`MyHelloWorldApp.csproj`**: The project configuration file (defines dependencies).
* **`App.xaml` / `App.xaml.cs**`: The entry point that starts the application.
* **`MainWindow.xaml`**: Where you paste the layout code I gave you earlier.
* **`MainWindow.xaml.cs`**: Where you paste the logic/button click code.

If you're looking for the C# version of the app you described (to compare with the Antigravity version we just did), the modern way to do this is using **WPF (Windows Presentation Foundation)**.

In modern C#, we can actually do this quite cleanly using a single-file approach or a standard XAML/C# split. Here is the straightforward implementation:

---

## Edit Layout (MainWindow.xaml)

This defines your "window," the "Hello World" label, the input slot, and the button.

```xml
<Window x:Class="HelloWorldApp.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MainWindow" Height="450" Width="800">
    <StackPanel Margin="20">
        <TextBlock x:Name="DisplayLabel" Text="Hello World!" FontSize="18" Margin="0,0,0,10" TextWrapping="Wrap"/>
        
        <TextBox x:Name="InputSlot" Margin="0,0,0,10" />
        <Button Content="Append Text" Click="OnAppendClick" Margin="0,0,0,10" />
        <Button Content="Clear Text" Click="OnClearClick"  Margin="0,0,0,10" />
        <Button Content="Send to Target App" Click="OnSendToAppClick" Margin="0,5,0,0" Background="LightBlue"/>
    </StackPanel>
</Window>

```

## The Logic (MainWindow.xaml.cs)

This handles the "click" event to grab the text and append it.

```csharp

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

```


---

## Adding the Required Reference

Since `SendKeys` lives in the "Windows Forms" library (even though we are using WPF), you need to tell your project to allow it.

Open your **`MyHelloWorldApp.csproj`** file and ensure it looks like this:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net10.0-windows</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <UseWPF>true</UseWPF>
    <UseWindowsForms>true</UseWindowsForms>
  </PropertyGroup>

</Project>

```

---

## Claeiry Library

Fix: 'Application' is an ambiguous reference between 'System.Windows.Forms.Application' and 'System.Windows.Application'

Open your **`MyHelloWorldApp.csproj`** file and ensure it looks like this:

```csharp
using System.Configuration;
using System.Data;
using System.Windows;

namespace autofill;

/// <summary>
/// Interaction logic for App.xaml
/// </summary>
public partial class App : System.Windows.Application
{
}

```


---

## Build Debug version

To compile C# from the command line, you have two main paths. The modern way uses the **.NET CLI** (cross-platform), while the classic way uses **CSC** (the direct C# Compiler).

Since you are setting up a WPF app, you should stick with the **.NET CLI** method, as it handles all the complex dependencies for windows and buttons automatically.


This is the standard for .NET 5, 6, 7, and 8. It uses a "Project" file (`.csproj`) to manage the compilation.

1. **Navigate** to your project folder:
```cmd
cd MyHelloWorldApp

```


2. **Restore** dependencies (downloads necessary libraries):
```cmd
dotnet restore

```


3. **Build** the project:
```cmd
dotnet build

```


* **Result:** Your `.exe` will be located in `bin\Debug\net8.0-windows\`.


---


## Explain: Find Target

This is where things get exciting—and a bit "hacky." To send text from your app to another window, you have to step outside the standard C# world and talk directly to the **Windows OS** using **P/Invoke** (Platform Invoke).

Because "clicking on another app" takes the focus away from your window, the most reliable way to do this is to:

1. **Wait** for a brief moment (to let you click the target app).
2. **Find** the active window.
3. **Simulate** keystrokes to "type" your text into that app.

 
---

## Explain: Input clear & simulate

To clear the existing content in the target app before "typing" your new text, we need to simulate the standard Windows keyboard shortcut for "Select All" (**Ctrl + A**) followed by **Backspace** or **Delete**.

In `SendKeys` terminology, the **Ctrl** key is represented by the caret symbol `^`.


---

### Important Details for `SendKeys`

If the target app is something like a browser address bar or Notepad, this works perfectly. However, keep these two things in mind:

* **Modifier Keys:** `SendKeys` uses special characters for modifiers:
* `^` = Ctrl
* `+` = Shift
* `%` = Alt


* **Timing:** Sometimes Windows is too fast for the target app to keep up. If you find it's only clearing the text but not typing the new text, you can add a tiny delay between the commands.

### Common Special Keys Table

| Action | SendKeys String |
| --- | --- |
| **Select All** | `^a` |
| **Copy** | `^c` |
| **Paste** | `^v` |
| **Enter** | `{ENTER}` |
| **Tab** | `{TAB}` |

---

### Final Check on Namespaces

Make sure you still have your alias at the top of the file so the compiler doesn't get confused again:
`using WinForms = System.Windows.Forms;`

Would you like to add a feature that automatically "minimizes" your C# window as soon as you click the button, so the target app is easier to see?



### A Note on "Antigravity" vs C#

Doing this in **Antigravity** (Python) is significantly easier because you can just use the `pyautogui` library:
`pyautogui.write(label.text)`.

In C#, you are dealing with the raw Windows API, which is more powerful but requires that "P/Invoke" setup we used above.

Would you like to try making it "Auto-Detect" the window so you don't have to wait 3 seconds? (This requires grabbing a list of running processes!)
