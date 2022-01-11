# BSDL
This is a python program to download files from BS.

# Requirements
* BSDL
  * Download the latest version of BSDL from the [releases](https://github.com/Quadrubo/BSDL/releases) tab.
  * Move it to wherever you like (It'll will other files so a placing it inside a folder will be necessary)

* Chrome Browser
  * Download the browser from [this](https://www.google.com/intl/de/chrome) website and install it.
  * Once installed, click on the profile icon in the top right corner, click add profile create one without an account and use any name you like.
    
* uBlock Origin
  * Download uBlock Origin from [this](https://chrome.google.com/webstore/detail/ublock-origin/cjpalhdlnbpafiamejdnhcphjbkeiagm) website and add it to chrome.
  * Open BS, click on uBlock Origin in the top right corner, click on more and enable popup blocking, press the lock to save it.

* ChromeDriver
  * Download the ChromeDriver from [this](https://chromedriver.chromium.org/downloads) website repository and move it anywhere you like.
  * If you don't know the version of Chrome you have, open "chrome://version".
   
* FFMPEG
  * Download FFMPEG from [this](https://github.com/BtbN/FFmpeg-Builds/releases) GitHub repository and save it anywhere you like.
  * Add the FFMPEG bin folder to your PATH environment variable.  
    
# Usage
  1) If you need help with the Configuration first, head to [this](https://github.com/Quadrubo/BSDL/blob/main/README.md#what-should-i-enter-on-the-config-page) section.
  2) Get a URL to a series from BS and paste it into the first field. Make sure that it has /1/de or /1/des etc. at the end. If not your selected language will not transfer.
  3) Click "Load..." to load the series.
  4) Now you should see every season and every episode that is available to download.
  5) Download them either individually using the "Download" Button or all together using the "Download all" Button.
  6) Solve any Captcha coming up on the website if necessary.
  7) Your downloaded episodes will be organized in the "_output" folder.
    
# Help
### What should I enter on the Config page?
  * Chrome user data directory: *Should be set automatically, you can see the directory in "chrome://version" under profile path (without the profile just User Data).*
  * Chrome profile directory: *Locate the profile in the user data directory folder, you can see the directory in "chrome://version" under profile path.*
  * Chrome driver file *Locate the chromedriver file you downloaded earlier.*
  * Hosters *Order the hosters as you please by dragging them, the top ones will be favourited if available.*

### That didn't help me.
  * Message me on Discord @ "Quadrubo#2536". I'm sure I can help you :)
    
