#!/bin/bash

cd docs/ && pip-compile requirements.in > requirements.txt && cd -
