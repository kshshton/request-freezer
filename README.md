`Freezer` is a basic sandbox that will allow you to save text content of the website to the **Redis** database.

![example](examples/example.png)

If you are using [WSL](https://learn.microsoft.com/en-us/windows/wsl/about), you can paste those functions into `$PROFILE` to make your life easier:
```powershell
function redis-start {wsl sudo service redis-server start}
function redis-stop {wsl sudo service redis-server stop}
function redis-status {wsl sudo service redis-server status}
function redis-clear {wsl redis-cli FLUSHALL}
```