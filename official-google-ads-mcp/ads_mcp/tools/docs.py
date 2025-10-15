# Copyright 2025 Google LLC
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

"""This module provides tools for accessing Google Ads API documentation."""

import os

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.utils import MODULE_DIR


@mcp.tool()
def get_gaql_doc() -> str:
  """Get Google Ads Query Language (GAQL) guides."""
  return get_gaql_doc_resource()


@mcp.resource("resource://Google_Ads_Query_Language")
def get_gaql_doc_resource() -> str:
  """Get Google Ads Query Language (GAQL) guides."""
  with open(
      os.path.join(MODULE_DIR, "context/GAQL.md"), "r", encoding="utf-8"
  ) as f:
    data = f.read()
  return data


@mcp.tool()
def get_reporting_view_doc(view: str | None) -> str:
  """Get Google Ads API reporting view docs.

  If a Google Ads API view resource is specific, the doc will include fields
  metadata for each the view.
  If a view is not specified, a doc briefs all views will be returned.

  Args:
      view: (Optional) The name of the view resource. If not set, a doc briefs
      all views will be returned.
  """
  if view:
    return get_view_doc(view)
  return get_reporting_doc()


@mcp.resource("resource://Google_Ads_API_Reporting_Views")
def get_reporting_doc() -> str:
  """Get Google Ads API reporting view docs."""
  with open(
      os.path.join(MODULE_DIR, "context/Google_Ads_API_Reporting_Views.md"),
      "r",
      encoding="utf-8",
  ) as f:
    data = f.read()
  return data


@mcp.resource("resource://views/{view}")
def get_view_doc(view: str) -> str:
  """Get resource view docs for a given Google Ads API view resource.

  Include fields metadata for each the view.

  Args:
      view: The name of the view resource.
  """
  try:
    with open(
        os.path.join(MODULE_DIR, f"context/views/{view}.yaml"),
        "r",
        encoding="utf-8",
    ) as f:
      data = f.read()
  except FileNotFoundError:
    return "No view resource with that name was found."
  return data
