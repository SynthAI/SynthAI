# Description:
#   Sunset: SynthAI abstractions for Neural Networks in TensorFlow.

package(default_visibility = ["//visibility:public"])

licenses(["notice"])  # Apache 2.0 License

exports_files(["LICENSE"])

py_library(
    name = "sunset",
    srcs = [
        "__init__.py",
    ],
    srcs_version = "PY2AND3",
    visibility = ["//visibility:public"],
    deps = [
        "//sunset/python:custom_getters",
        "//sunset/python:modules",
        "//sunset/python:ops",
        # tensorflow dep,
    ],
)
