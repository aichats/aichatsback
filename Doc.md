# Developer Toolbook

# [Flake8](https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html)

1. Ignore On Line

```python
example = lambda: 'example'  # noqa: E731
```

2. Ignore File

```python
# flake8: noqa: F403

```

3. Ignore Fake Config

```setup.cfg
[flake8]
per-file-ignores =
    test_*.py: F403, F405, E701, F841,E501,F401,E731
    *.py: E501, F401,E731
```
