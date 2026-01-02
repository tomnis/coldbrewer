

conf = """
version: 1
disable_existing_loggers: False

formatters:
  colored:
    # Use Uvicorn's ColourizedFormatter class directly
    class: uvicorn.logging.ColourizedFormatter
    # Define the format string using the 'style' attribute to enable curly brace formatting
    format: "{levelprefix:<8} | {asctime} | {name} | {message}"
    style: "{"
    # Explicitly enable colors
    use_colors: True
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    formatter: colored # Reference the colored formatter
    stream: ext://sys.stdout

loggers:
  "": # root logger
    handlers: [console]
    level: INFO
    propagate: False
  uvicorn.error:
    level: INFO
    handlers: [console]
    propagate: False
  uvicorn.access:
    level: INFO
    handlers: [console]
    propagate: False
"""