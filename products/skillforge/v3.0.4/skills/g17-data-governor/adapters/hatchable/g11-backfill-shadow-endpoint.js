import { g11GraphPreflight, g11Backfill } from 'lib/g11-graph-list-backfill.js';

export const access = 'admin';
export const methods = ['POST'];

export default async function(req, res) {
  const body = req.body || {};
  try {
    if (body.mode === 'graph_preflight') {
      return res.json(await g11GraphPreflight());
    }
    const mode = body.mode === 'backfill' ? 'backfill' : 'preflight';
    const maxPerList = Number.isFinite(Number(body.maxPerList)) && Number(body.maxPerList) > 0
      ? Math.min(Number(body.maxPerList), 10000)
      : null;
    const result = await g11Backfill({ mode, maxPerList });
    return res.status(result.ok ? 200 : 409).json(result);
  } catch (error) {
    return res.status(503).json({
      ok: false,
      error: error?.code || 'G11_GRAPH_BACKFILL_FAILED',
      detail: error?.detail || null
    });
  }
}
