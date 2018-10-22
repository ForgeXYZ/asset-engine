# Asset Engine - Pipeline Core

## Setup

### Clone this repository

```bash
git clone https://github.com/lvxejay/asset-engine.git
```

### Run the Pipe Context Unit Test

```bash
cd asset-engine
python -m unittest tests/test_pipe_context.py
```

## Usage

### Pipeline Context

The `PipeContext` class is the main entry point for this package. Give the `get_path()` method a `formula` defined in any of the `*formulas.txt` files to return a path on disk.

- Example: `PipeContext.get_path(formula="pipe_base_dir", *args, **kwargs)`

    ```py
    from pipe_context import PipeContext as PC
    pipe_base_dir = '/home/user/pipeline'

    # Get a path from PipeContext
    """
    ::get_path(formula="pipe_base_dir", *args, **kwargs)

    Evaluate a formula and return a path
    :param formula:
    :param args: positional arguments, e.g. parent_formula
    :param kwargs: keyword_arguments to pass to PipeContext
    :return: path
    """
    path = PC.get_path(
                'pr_base_dir',
                drive=pipe_base_dir, project='avengers',
                asset_type='alien', asset="nova_prime_soldier"
                )
    ```

Note: Most `Asset` level formulas will require additional *parent* formulas (e.g. `pr_as_type_dir`) in order to resolve correctly.

- Example: Asset Texture Directory -> `as_tex_dir`

    ```py
    # Requires additional positional argument `pr_as_type_dir`
    path = PC.get_path(
                'as_tex_dir', 'pr_as_type_dir',
                drive=pipe_base_dir, project='project_2',
                asset_type='architecture', asset="empire_state_building"
            )
    ```

PipeContext also has built-in context-manager functionality. It will store, remember and update its internal context reference path within any `with` statement. Check out the Multi-Path test to see the implementation in action.

- Example:

    ```py
    class PipeContext(AbstractContextManager):
            def __enter__(self):
            """
            Upon entering the PipeContext Manager, current context is assigned to the platform specific base drive
            """
            self.context = self.drive
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            """
            Upon exiting the PipeContext Manager, current context is set to the most recently cached context
            :return:
            """
            self.old_context.pop()
            pass

    PCTX = PipeContext()
    with PCTX:
        path = PCTX.eval_path(formula, *args, **kwargs)
        print(path)
        print(PCTX.context)
    ```

## Repository Details

```bash
├── data
│       └── Formulas
├── path_lib.py
│       └──  Path library
├── pipe_context.py
│       └── Context Manager
├── pipe_enums.py
│       └── Enumerators and Constants
├── pipe_utils.py
│       └── Extra utilities
└── tests
```
