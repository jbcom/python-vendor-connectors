=========================================
vendor-connectors Documentation
=========================================

Universal vendor connectors for the jbcom ecosystem, providing standardized access to:

- **Cloud Providers**: AWS, Google Cloud
- **Services**: GitHub, Slack, Vault, Zoom
- **AI APIs**: Anthropic Claude, Cursor agents, Meshy 3D

Features
--------

- **Unified API**: Consistent interface across all vendors
- **AI Tools**: LangChain, CrewAI, and Strands integration
- **MCP Servers**: Model Context Protocol support for AI agents
- **Credential Management**: Automatic loading from env vars, files, or stdin

Quick Example
-------------

.. code-block:: python

   from vendor_connectors.aws.tools import get_tools

   # Get AWS tools for your AI framework
   tools = get_tools()  # Auto-detects LangChain, CrewAI, or Strands

   # Or use connectors directly
   from vendor_connectors.aws import AWSConnectorFull
   
   connector = AWSConnectorFull()
   secrets = connector.list_secrets()

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   getting-started/installation
   getting-started/quickstart

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/contributing
   development/building-connector-tools

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
