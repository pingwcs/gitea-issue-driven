# Comment pagination fallback

Load this only when the active phase contract permits it and the selected connector cannot prove a complete issue-comment read.

Compare returned comments with the issue's comment count when available. If completeness remains unknown, use the already selected local Tea login's authenticated `api` command only to paginate comments, then merge results by comment ID.

MCP remains primary. Tea is read-only in this fallback: do not use it for writes, general REST access, connector reconfiguration, or alternate credential discovery. Treat a denied or unavailable fallback as missing required evidence.
