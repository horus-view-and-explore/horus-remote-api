# Installation

## Linux

Follow [Using Python on Unix platforms][pyunix].


## Windows

1. Install Python 3.9 from the Microsoft Store. Or follow the
   [Using Python on Windows][pywin] guide.

2. Enable UTF-8 for Python by adding `PYTHONUTF8=1` to the environment
   variables.

3. Add Python's script path to the `Path` environment variable. You can
   get the script path by running the following snippet in the
   PowerShell or command prompt:

   ```
   python -c 'import site; print(site.USER_BASE + \"\\Python39\\Scripts\")'
   ```

See [Excursus: Setting environment variables][pywinenv] for instructions
on setting environment variables.


## Install horus-remote-api

### Using pip

You can install horus-remote-api directly from GitHub:

```
pip install "https://github.com/horus-view-and-explore/horus-remote-api/archive/refs/heads/main.zip"
```

Or the following when you have git installed:


```
pip install "git+https://github.com/horus-view-and-explore/horus-remote-api.git#egg=horus_remote_api"
```

Alternatively, you can clone the repository, go into the horus-remote-api
directory and run:

```
pip install -U .
```

When you're developing run the following instead:

```
pip install --editable .
```

Changes to the source code then require not reinstall.

NOTE: On Windows `pip` is called with `pip.exe`.


[pyunix]: https://docs.python.org/3/using/unix.html
[pywin]: https://docs.python.org/3/using/windows.html
[pywinenv]: https://docs.python.org/3/using/windows.html#setting-envvars
