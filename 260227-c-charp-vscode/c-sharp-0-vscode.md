# C# basic

For research purposes, **Python** is the most convenient choice due to its vast ecosystem of community-developed libraries and AI tools. However, since most enterprises prefer the **Windows** environment, **C#** is often the more suitable language for developing internal tools. While the industry-standard development environment is **Visual Studio**, **VS Code** offers a much more lightweight alternative for non-professional development units.

In terms of user experience on non-Windows systems, tools like **Antigravity** or **Claude** often provide superior direct support for VS Code compared to Copilot. That said, without corporate approval, these tools remain off-limits. Consequently, we rely on the more traditional method of using AI as a reference for code generation and then manually adapting it to fit our specific requirements.

Since VS Code is not the primary environment Microsoft promotes for C# development, documentation can be sparse. This guide documents how to build a **C# application (.exe)** using the command-line interface (CLI).

---

## Install .NET SDK


### Step 1: Download the SDK

You need to download the **.NET SDK** (not just the "Runtime").

1. Go to the [official .NET download page](https://dotnet.microsoft.com/download).
2. Look for **.NET 10.0** (or the latest Long Term Support version).
3. Click the **Windows x64** installer.
4. Run the `.exe` and follow the "Next, Next, Finish" prompts.



### Step 2: Refresh your Terminal

**Important:** Once the installation finishes, you **must** close and restart any open Command Prompt or VS Code windows. They won't recognize the new command until they are restarted.

1. Close VS Code.
2. Open a **new** `cmd.exe`.
3. Type: `dotnet --version`
* If it returns a number (like `10.0.xxx`), you’re ready to go!



### Step 3: Troubleshooting the "Path"

If you’ve installed it and restarted, but still see the error, you may need to manually verify the installation folder:

1. Open your File Explorer and go to: `C:\Program Files\dotnet`
2. If that folder exists and has a `dotnet.exe` inside, but `cmd` still fails, you need to add that path to your **System Environment Variables**.



### Step 4: Re-run your commands

Once `dotnet --version` works, go back to your project folder in the terminal and try the creation command again:

```bash
dotnet new wpf -n MyHelloWorldApp

```


---
## Install .NET extention on **VS Code** 


To get a C# WPF application running in **VS Code** (which is a bit different than the full Visual Studio), you’ll need a few specific tools to handle the project structure and the compilation into an `.exe`.

---

### 1. Essential VS Code Extensions

Open the Extensions view (`Ctrl+Shift+X`) and install:

* **C# Dev Kit:** The official Microsoft extension for C# development.
* **.NET Install Tool:** Usually comes with the C# Dev Kit; ensures you have the proper runtime.

---

### 2. File Structure via Terminal

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

---

### 3. How to Create the .exe  

To compile C# from the command line, you have two main paths. The modern way uses the **.NET CLI** (cross-platform), while the classic way uses **CSC** (the direct C# Compiler).

Since you are setting up a WPF app, you should stick with the **.NET CLI** method, as it handles all the complex dependencies for windows and buttons automatically.



### Method 1: The Modern Way (.NET CLI)

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





### Method 2: The "Publish" Way (For Distribution)

If you want a single file to give to a friend, use the **Publish** command. This is the most "complete" form of compilation.

```cmd
dotnet publish -c Release -r win-x64 --self-contained true /p:PublishSingleFile=true  /p:IncludeNativeLibrariesForSelfExtract=true

```

**Why use this instead of `dotnet build`?**

* **Build:** Creates a bunch of `.dll` files and requires the user to have .NET installed.
* **Publish:** Crushes everything into one icon that works on any Windows PC.



**Breakdown of that command:**

* **`-c Release`**: Optimizes the code for performance.
* **`-r win-x64`**: Targets Windows 64-bit.
* **`--self-contained true`**: Includes the .NET runtime so the user doesn't have to install anything to run it.
* **`-p:PublishSingleFile=true`**: Bundles everything into **one single `.exe` file**.
* **`-p:IncludeNativeLibrariesForSelfExtract=true`**: With previous settings, possibly there're still libraries left out. This setting helps.



**Where to find your file**

After running the publish command, navigate to:
`bin/Release/netX.X/win-x64/publish/`

You will see **`MyHelloWorldApp.exe`**. You can now send this file to anyone on Windows, and it will run your "Hello World" app!

#### Pro-Tip: XAML Preview

VS Code does not have a "Drag and Drop" visual designer for WPF. Most C# developers use **Visual Studio Community** for UI work because of the visual editor, but in VS Code, you'll be writing the XAML manually and running the app to see the changes.


---

### Summary Table

| Goal | Command | Best For |
| --- | --- | --- |
| **Testing** | `dotnet run` | Compiles and starts the app immediately. |
| **Development** | `dotnet build` | Checking for errors during coding. |
| **Final Product** | `dotnet publish` | Creating the final `.exe` for users. |

**Quick Tip:** If `dotnet` still isn't working in your CMD, try typing `where dotnet`. If it says "Information could not be found," the installation from the previous step hasn't registered in your System Path yet.


## 1st C# app


In modern C#, we can actually do this quite cleanly using a single-file approach or a standard XAML/C# split. Here is the straightforward implementation:

---

### 1. The Layout (MainWindow.xaml)

This defines your "window," the "Hello World" label, the input slot, and the button.

```xml
<Window x:Class="HelloWorldApp.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="My C# App" Height="250" Width="400">
    <StackPanel Margin="20">
        <TextBlock x:Name="DisplayLabel" Text="Hello World!" FontSize="18" Margin="0,0,0,10" TextWrapping="Wrap"/>
        
        <TextBox x:Name="InputSlot" Margin="0,0,0,10" />
        <Button Content="Append Text" Click="OnAppendClick" />
    </StackPanel>
</Window>

```

### 2. The Logic (MainWindow.xaml.cs)

This handles the "click" event to grab the text and append it.

```csharp
using System.Windows;

namespace HelloWorldApp
{
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
}

```

---

### Key Concepts in this Code

* **StackPanel:** This is a layout container that stacks elements vertically (similar to `direction="column"` in Antigravity).
* **x:Name:** This is how we give an element a "name" so that our C# code can find it and change its text.
* **Events:** The `Click="OnAppendClick"` attribute connects the button in the UI to the function in your code.

### Simple Console Version

If you didn't want a window and just wanted the most basic "Hello World" possible in modern C# (Version 9.0+), it’s just one line:

```csharp
System.Console.WriteLine("Hello, World!");

```

Would you like me to explain how to compile this C# code into an actual `.exe` file, or should we look at how to add some "Antigravity" style animations to the Python version?