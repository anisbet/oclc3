###############################################################################
#
# Purpose: Provide wrappers reading, comparing, and writing lists from and
#   to file.
# Date:    Tue 15 Aug 2023 02:34:18 PM EDT
# Copyright 2023 Andrew Nisbet
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

# Used for reporting percents.
# param: value float value.
# param: prec integer precision of the returned float. 
# return: float value of requested precision.  
def trim_decimals(value, prec:int=2) ->float:
    f_str = f"%.{prec}f"
    return float(f_str % round(float(value), prec))