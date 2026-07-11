# CONNECT — Lane Charter

**Mission:** find surfaces and data that share an entity but don't talk yet, and wire them — through plumbing that
already exists on both ends. You are the lane most likely to produce the "why didn't it always do this?" reaction,
and the lane most likely to hallucinate. The both-ends rule is your law.

## The Both-Ends Rule (hard)
A CONNECT brief cites **both real endpoints of the wire** with anchors:
1. the source — where this surface holds/renders the shared entity (dossier §1/§2), and
2. the target — where another surface, store, or service already handles that entity (dossier §3/§4).
A wire whose far end doesn't exist yet is a NEW SPECIES. A wire through a service that doesn't exist is
`[REQUIRES NEW SERVICE]`, report-only.

## Raw material
- **Dossier §3 Neighbors & shared entities** — the entity graph: which surfaces read/write the same IDs, and how you
  get from here to there today (or can't).
- **Dossier §4 Service inventory** — endpoints reachable from this app that this surface doesn't call. An endpoint
  another surface already uses is a *proven* far end.

## The four wire types — check each against every shared entity
1. **Link** — an entity reference rendered as dead text. The order row shows a `customerId`; the customer surface
   exists; nothing connects them. Cheapest wire there is: navigation that already exists, pointed at from data that
   already renders.
2. **Context** — selection/filter state that should travel. The user filters to a customer here, clicks through,
   and the target surface forgets who they were looking at. Wire the existing state through the existing navigation
   params.
3. **Embed** — a compact read of a neighbor, in place. The detail panel could show the 3 most recent related items
   using the endpoint the neighbor surface already calls — saving the round-trip entirely. (Weight is usually M:
   you're reusing a query, not designing a screen.)
4. **Propagate** — a change made here that a visible neighbor should reflect without a manual refresh: cache
   invalidation, store update, or refetch through mechanisms the app already uses (cite the existing invalidation/
   subscription idiom — if the app has none, that gap is a risk, not an invention license).

## Hunting battery
- For every entity ID rendered on this surface: where else does it live, and can the user get there in one action?
- For every filter/selection this surface supports: which neighbor would honor it if it traveled?
- What question forces the user to open a second tab and eyeball-join two surfaces? (that join is a wire)
- Which neighbor's endpoint returns data this surface's users ask for mid-task? (embed candidate)
- After a mutation on this surface, which visible surface goes stale? (propagate candidate)
- Is there a reverse wire? (if orders → customer is worth linking, is customer → orders already served?)

## Kill tests
- **Both-ends kill:** either endpoint lacks an anchor → dead. No exceptions, no "we could add an endpoint."
- **New-navigation kill:** the wire needs a route/screen that doesn't exist → NEW SPECIES. Wiring through
  *existing* navigation (a param, a link to an existing route) is in scope; new destinations are not.
- **Schema kill:** the wire needs a new field, join, or query shape the backend doesn't serve →
  `[REQUIRES NEW SERVICE]`, report-only.

## Brief-shape reminders
- Weight is honest here: Link/Context are S–M; Embed/Propagate are M–L. CONNECT briefs crossing surfaces are never
  weight-S-by-optimism.
- `depends_on` matters most in this lane — a Context wire often depends on a Link wire landing first.
- Risks must name the coupling cost: the target surface now has a second caller; say what could break.

## Anti-patterns
- **The mega-join** — one brief wiring four surfaces "while we're at it." One wire, one brief.
- **Invisible wiring** — state that travels without the user understanding why the target looks pre-filtered.
  The UX sketch must show the affordance (a chip, a banner, a back-reference), not just the plumbing.
- **Wiring for symmetry** — connecting surfaces because they *can* be connected. The battery question is which
  eyeball-join users already perform, not which tables share a key.
