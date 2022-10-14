# Installation

## Run in WSL to install service:
```
sudo apt install linux-tools-5.4.0-77-generic hwdata
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/5.4.0-77-generic/usbip 20
```

## Install usbip on windows
```
winget install --interactive --exact dorssel.usbipd-win
```

# Management

Run in powershell with admin rights

## List USB devices in windows:
```
usbipd wsl list
```

## Attatch USB device to wsl:
```
usbipd wsl attach --busid <busid>
```

## Detatch USB device from wsl:
```
usbipd wsl detatch --busid <busid>
```