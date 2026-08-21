#!/usr/bin/env python3
"""
LS-DYNA mesh generator
  Drone (quadcopter) high-speed impact + battery burst on a 2-story
  commercial (retail) building.

Consistent unit system:  kg - mm - ms - kN - GPa
  length      mm
  time        ms
  mass        kg
  force       kN
  stress      GPa      (1 GPa = 1000 MPa)
  density     kg/mm^3  (steel = 7.85e-6)
  velocity    mm/ms    ( = m/s )
  gravity     9.81e-3  mm/ms^2
  energy      kJ

Writes:
  building.k   nodes / shells / beams / base node set
  drone.k      nodes / shells / solids
  blast.inc    *LOAD_BLAST_ENHANCED + *LOAD_BLAST_SEGMENT_SET + segment sets
               (deliberately NOT named .k - the OpenRadioss reader picks up
                stray .k files in the run directory and then errors on the
                blast keywords it cannot map)
"""

import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# user-tunable mesh sizes
# ----------------------------------------------------------------------------
H_BLD = 250.0      # building shell size  [mm]
H_GND = 1000.0     # ground plane size    [mm]
H_DRN = 10.0       # drone shell/solid    [mm]

# ----------------------------------------------------------------------------
# building geometry
# ----------------------------------------------------------------------------
BW = 12000.0       # width  (X)
BD =  8000.0       # depth  (Y)   facade at Y = 0
H1 =  3500.0       # 1F storey height
H2 =  7000.0       # roof level

# facade horizontal bands (Z)
Z_BASE_T = 500.0    # 0     -> 500     concrete bulkhead
Z_G1_T   = 3250.0   # 500   -> 3250    1F storefront glass
Z_SPD_T  = 3750.0   # 3250  -> 3750    spandrel band (2F slab edge)
Z_G2_T   = 6750.0   # 3750  -> 6750    2F glass   <-- impact target
# 6750 -> 7000 parapet

COL_X = [0.0, 4000.0, 8000.0, 12000.0]
COL_Y = [0.0, 4000.0, 8000.0]

# ----------------------------------------------------------------------------
# drone placement / flight
# ----------------------------------------------------------------------------
DX, DY, DZ = 6000.0, -570.0, 5000.0    # drone body centre, global
V_IMPACT   = 40.0                      # mm/ms  ( = 40 m/s )

# ----------------------------------------------------------------------------
# part ids
# ----------------------------------------------------------------------------
P_COL, P_GIR, P_SLAB2, P_ROOF   = 101, 102, 103, 104
P_BAND, P_GL1, P_GL2, P_MUL     = 105, 106, 107, 108
P_WALL, P_GND                   = 109, 110

P_BODY, P_ARM, P_MOTOR          = 201, 202, 203
P_PROP, P_BATT, P_GIMB          = 204, 205, 206

SID_BASE_NODES = 1
SID_SEG_FACADE = 901
SID_SEG_DRONE  = 902
SID_SEG_ALL    = 903
SID_SHL_BODY   = 210      # drone body shells - burst pressure in the OpenRadioss deck


# ============================================================================
class Mesh:
    def __init__(self, nid0, eid_sh, eid_so, eid_be):
        self.nid, self.index, self.nodes = nid0, {}, []
        self.shells, self.solids, self.beams = [], [], []
        self.es, self.eso, self.eb = eid_sh, eid_so, eid_be

    # -- nodes ---------------------------------------------------------------
    def n(self, x, y, z):
        """merged node (shared geometry is welded automatically)"""
        k = (round(x, 3), round(y, 3), round(z, 3))
        i = self.index.get(k)
        if i is None:
            i = self.nid
            self.nid += 1
            self.index[k] = i
            self.nodes.append((i, x, y, z))
        return i

    def fn(self, x, y, z):
        """free node, never merged (beam orientation nodes, ground plane)"""
        i = self.nid
        self.nid += 1
        self.nodes.append((i, x, y, z))
        return i

    # -- elements ------------------------------------------------------------
    def shell(self, pid, a, b, c, d):
        self.shells.append((self.es, pid, a, b, c, d)); self.es += 1

    def solid(self, pid, nn):
        self.solids.append((self.eso, pid, nn)); self.eso += 1

    def beam(self, pid, a, b, c):
        self.beams.append((self.eb, pid, a, b, c)); self.eb += 1

    # -- primitives ----------------------------------------------------------
    def plate(self, pid, o, du, dv, nu, nv, dedup=True):
        """planar shell patch; outward normal = du x dv"""
        mk = self.n if dedup else self.fn
        g = [[mk(o[0] + du[0]*i + dv[0]*j,
                 o[1] + du[1]*i + dv[1]*j,
                 o[2] + du[2]*i + dv[2]*j) for j in range(nv+1)]
             for i in range(nu+1)]
        quads = []
        for i in range(nu):
            for j in range(nv):
                q = (g[i][j], g[i+1][j], g[i+1][j+1], g[i][j+1])
                self.shell(pid, *q)
                quads.append(q)
        return quads

    def box_shell(self, pid, x0, x1, y0, y1, z0, z1, h, faces="all"):
        """hollow box of shells, all normals pointing outward"""
        nx, ny, nz = int(round((x1-x0)/h)), int(round((y1-y0)/h)), int(round((z1-z0)/h))
        if faces == "all":
            faces = ("x0", "x1", "y0", "y1", "z0", "z1")
        q = []
        if "x0" in faces: q += self.plate(pid, (x0,y0,z0), (0,0,h), (0,h,0), nz, ny)
        if "x1" in faces: q += self.plate(pid, (x1,y0,z0), (0,h,0), (0,0,h), ny, nz)
        if "y0" in faces: q += self.plate(pid, (x0,y0,z0), (h,0,0), (0,0,h), nx, nz)
        if "y1" in faces: q += self.plate(pid, (x0,y1,z0), (0,0,h), (h,0,0), nz, nx)
        if "z0" in faces: q += self.plate(pid, (x0,y0,z0), (0,h,0), (h,0,0), ny, nx)
        if "z1" in faces: q += self.plate(pid, (x0,y0,z1), (h,0,0), (0,h,0), nx, ny)
        return q

    def box_solid(self, pid, x0, x1, y0, y1, z0, z1, h):
        nx, ny, nz = int(round((x1-x0)/h)), int(round((y1-y0)/h)), int(round((z1-z0)/h))
        g = [[[self.n(x0+i*h, y0+j*h, z0+k*h) for k in range(nz+1)]
              for j in range(ny+1)] for i in range(nx+1)]
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    self.solid(pid, (g[i][j][k],     g[i+1][j][k],
                                     g[i+1][j+1][k], g[i][j+1][k],
                                     g[i][j][k+1],   g[i+1][j][k+1],
                                     g[i+1][j+1][k+1], g[i][j+1][k+1]))
        return g

    def beam_line(self, pid, p0, p1, ne, ovec):
        """string of beam elements from p0 to p1, ovec = local-s reference dir"""
        d = [(p1[i]-p0[i])/ne for i in range(3)]
        pts = [self.n(p0[0]+d[0]*i, p0[1]+d[1]*i, p0[2]+d[2]*i) for i in range(ne+1)]
        mid = ((p0[0]+p1[0])/2, (p0[1]+p1[1])/2, (p0[2]+p1[2])/2)
        n3 = self.fn(mid[0]+ovec[0], mid[1]+ovec[1], mid[2]+ovec[2])
        for i in range(ne):
            self.beam(pid, pts[i], pts[i+1], n3)
        return pts


# ============================================================================
# writers
# ============================================================================
def w_nodes(f, nodes):
    f.write("*NODE\n")
    f.write("$#   nid               x               y               z      tc      rc\n")
    for i, x, y, z in nodes:
        f.write("%8d%16.4f%16.4f%16.4f\n" % (i, x, y, z))


def w_shells(f, shells):
    if not shells:
        return
    f.write("*ELEMENT_SHELL\n")
    f.write("$#   eid     pid      n1      n2      n3      n4\n")
    for e in shells:
        f.write("%8d%8d%8d%8d%8d%8d\n" % e)


def w_solids(f, solids):
    if not solids:
        return
    f.write("*ELEMENT_SOLID\n")
    f.write("$#   eid     pid\n$#    n1      n2      n3      n4      n5      n6      n7      n8\n")
    for e, p, nn in solids:
        f.write("%8d%8d\n" % (e, p))
        f.write("".join("%8d" % v for v in nn) + "\n")


def w_beams(f, beams):
    if not beams:
        return
    f.write("*ELEMENT_BEAM\n")
    f.write("$#   eid     pid      n1      n2      n3\n")
    for e in beams:
        f.write("%8d%8d%8d%8d%8d\n" % e)


def w_set_node(f, sid, ids):
    f.write("*SET_NODE_LIST\n")
    f.write("$#     sid       da1       da2       da3       da4\n")
    f.write("%10d\n" % sid)
    ids = sorted(ids)
    for i in range(0, len(ids), 8):
        f.write("".join("%10d" % v for v in ids[i:i+8]) + "\n")


def w_set_shell(f, sid, eids):
    f.write("*SET_SHELL_LIST\n")
    f.write("$#     sid       da1       da2       da3       da4\n")
    f.write("%10d\n" % sid)
    eids = sorted(eids)
    for i in range(0, len(eids), 8):
        f.write("".join("%10d" % v for v in eids[i:i+8]) + "\n")


def w_set_segment(f, sid, quads):
    f.write("*SET_SEGMENT\n")
    f.write("$#     sid       da1       da2       da3       da4\n")
    f.write("%10d\n" % sid)
    f.write("$#      n1        n2        n3        n4\n")
    for q in quads:
        f.write("".join("%10d" % v for v in q) + "\n")


# ============================================================================
# BUILDING
# ============================================================================
def build_building():
    m = Mesh(nid0=100001, eid_sh=1, eid_so=150001, eid_be=200001)
    h = H_BLD

    nx = int(BW / h)          # 48
    ny = int(BD / h)          # 32
    nz = int(H2 / h)          # 28

    # ---- front facade (Y = 0), normals -> -Y (outward, toward the drone) ----
    def band(pid, z0, z1):
        return m.plate(pid, (0.0, 0.0, z0), (h, 0, 0), (0, 0, h),
                       nx, int(round((z1-z0)/h)))

    q_band = []
    q_band += band(P_BAND, 0.0,      Z_BASE_T)   # bulkhead
    q_glass1 = band(P_GL1, Z_BASE_T, Z_G1_T)     # 1F storefront glazing
    q_band += band(P_BAND, Z_G1_T,   Z_SPD_T)    # spandrel
    q_glass2 = band(P_GL2, Z_SPD_T,  Z_G2_T)     # 2F glazing  <-- target
    q_band += band(P_BAND, Z_G2_T,   H2)         # parapet

    # ---- side + rear walls (masonry infill) --------------------------------
    m.plate(P_WALL, (0.0,  0.0, 0.0), (0, 0, h), (0, h, 0), nz, ny)      # X=0
    m.plate(P_WALL, (BW,   0.0, 0.0), (0, h, 0), (0, 0, h), ny, nz)      # X=BW
    m.plate(P_WALL, (0.0,  BD,  0.0), (0, 0, h), (h, 0, 0), nz, nx)      # Y=BD

    # ---- floor slabs -------------------------------------------------------
    m.plate(P_SLAB2, (0.0, 0.0, H1), (h, 0, 0), (0, h, 0), nx, ny)
    m.plate(P_ROOF,  (0.0, 0.0, H2), (h, 0, 0), (0, h, 0), nx, ny)

    # ---- RC columns --------------------------------------------------------
    for cx in COL_X:
        for cy in COL_Y:
            m.beam_line(P_COL, (cx, cy, 0.0), (cx, cy, H2), nz, (137.0, 0.0, 0.0))

    # ---- RC girders --------------------------------------------------------
    for zl in (H1, H2):
        for cy in COL_Y:                                   # spanning X
            m.beam_line(P_GIR, (0.0, cy, zl), (BW, cy, zl), nx, (0.0, 0.0, 137.0))
        for cx in COL_X:                                   # spanning Y
            m.beam_line(P_GIR, (cx, 0.0, zl), (cx, BD, zl), ny, (0.0, 0.0, 137.0))

    # ---- curtain-wall mullions (aluminium) ---------------------------------
    for i in range(0, 13):
        mx = i * 1000.0
        m.beam_line(P_MUL, (mx, 0.0, 0.0), (mx, 0.0, H2), nz, (0.0, 137.0, 0.0))

    # ---- rigid ground plane (top face at Z=-1, not merged to the frame) ----
    m.plate(P_GND, (-4000.0, -4000.0, -11.0), (H_GND, 0, 0), (0, H_GND, 0),
            int(20000/H_GND), int(16000/H_GND), dedup=False)

    # ---- base node set (everything at Z = 0 of the frame) ------------------
    base = [i for (i, x, y, z) in m.nodes if abs(z) < 1e-6]

    # facade segment set for the blast: reversed normals (+Y, interior facing),
    # because the charge ends up at / just inside the perforated wall.
    seg_facade = [(a, d, c, b) for (a, b, c, d) in (q_glass1 + q_glass2 + q_band)]

    with open(os.path.join(OUT, "building.k"), "w") as f:
        f.write("$# 2-story commercial building - generated by generate_model.py\n")
        f.write("$# units: kg - mm - ms - kN - GPa\n")
        w_nodes(f, m.nodes)
        w_shells(f, m.shells)
        w_beams(f, m.beams)
        w_set_node(f, SID_BASE_NODES, base)
        f.write("$# end building.k\n")

    # the segment set itself is written into blast.k, right after the card that
    # uses it, so no *LOAD_BLAST_SEGMENT_SET card is ever the last thing in a file
    return m, len(base), seg_facade


# ============================================================================
# DRONE  (quadcopter, "+" layout, ~2.2 kg, 700 mm motor-to-motor)
# ============================================================================
def build_drone():
    m = Mesh(nid0=500001, eid_sh=300001, eid_so=400001, eid_be=250001)
    h = H_DRN

    def X(v): return DX + v
    def Y(v): return DY + v
    def Z(v): return DZ + v

    # ---- central body shell (200 x 200 x 80) -------------------------------
    q_body = m.box_shell(P_BODY, X(-100), X(100), Y(-100), Y(100), Z(-40), Z(40), h)

    # ---- 4 arms: 20 x 20 square CFRP tubes, root welded into the body ------
    m.box_shell(P_ARM, X(-10), X(10), Y(100),  Y(350),  Z(-10), Z(10), h,
                faces=("x0", "x1", "z0", "z1", "y1"))
    m.box_shell(P_ARM, X(-10), X(10), Y(-350), Y(-100), Z(-10), Z(10), h,
                faces=("x0", "x1", "z0", "z1", "y0"))
    m.box_shell(P_ARM, X(100),  X(350),  Y(-10), Y(10), Z(-10), Z(10), h,
                faces=("y0", "y1", "z0", "z1", "x1"))
    m.box_shell(P_ARM, X(-350), X(-100), Y(-10), Y(10), Z(-10), Z(10), h,
                faces=("y0", "y1", "z0", "z1", "x0"))

    # ---- motors (40 x 40 x 30 solid blocks on the arm tips) ----------------
    m.box_solid(P_MOTOR, X(-20), X(20), Y(310),  Y(350),  Z(10), Z(40), h)
    m.box_solid(P_MOTOR, X(-20), X(20), Y(-350), Y(-310), Z(10), Z(40), h)
    m.box_solid(P_MOTOR, X(310),  X(350),  Y(-20), Y(20), Z(10), Z(40), h)
    m.box_solid(P_MOTOR, X(-350), X(-310), Y(-20), Y(20), Z(10), Z(40), h)

    # ---- propellers (flat blades welded on the motor tops) -----------------
    nb = int(260/h)
    m.plate(P_PROP, (X(-130), Y(310),  Z(40)), (h, 0, 0), (0, h, 0), nb, 2)
    m.plate(P_PROP, (X(-130), Y(-350), Z(40)), (h, 0, 0), (0, h, 0), nb, 2)
    m.plate(P_PROP, (X(310),  Y(-130), Z(40)), (h, 0, 0), (0, h, 0), 2, nb)
    m.plate(P_PROP, (X(-350), Y(-130), Z(40)), (h, 0, 0), (0, h, 0), 2, nb)

    # ---- LiPo battery pack (160 x 60 x 40) on the body floor ---------------
    m.box_solid(P_BATT, X(-80), X(80), Y(-30), Y(30), Z(-40), Z(0), h)
    n_batt = m.n(X(0.0), Y(0.0), Z(-20.0))     # blast origin follows this node

    # ---- gimbal / camera pod under the nose --------------------------------
    m.box_solid(P_GIMB, X(-30), X(30), Y(40), Y(100), Z(-80), Z(-40), h)

    # body inner surface for the internal blast: reversed (inward) normals
    seg_drone = [(a, d, c, b) for (a, b, c, d) in q_body]

    with open(os.path.join(OUT, "drone.k"), "w") as f:
        f.write("$# quadcopter UAV - generated by generate_model.py\n")
        f.write("$# units: kg - mm - ms - kN - GPa\n")
        w_nodes(f, m.nodes)
        w_shells(f, m.shells)
        w_solids(f, m.solids)
        f.write("$# 210 = body shells; the OpenRadioss deck puts the burst\n")
        f.write("$#       pressure here (*LOAD_SHELL_SET), since OpenRadioss\n")
        f.write("$#       does not read *LOAD_BLAST_ENHANCED\n")
        w_set_shell(f, SID_SHL_BODY, [e for (e, pid, a, b, c, d) in m.shells
                                      if pid == P_BODY])
        f.write("$# end drone.k\n")

    return m, n_batt, seg_drone


# ============================================================================
def write_blast(nid_batt, seg_facade, seg_drone):
    """LiPo thermal-runaway burst, modelled as a small TNT-equivalent charge
    that travels with the battery (NIDBO).

    Layout matters here:
      * ONE *LOAD_BLAST_SEGMENT_SET card referencing ONE merged segment set
        (903) - a single blast id loaded through a single set.
      * every field written explicitly, no blank trailing fields.
      * the *SET_SEGMENT blocks come AFTER the load cards, so the load card is
        always followed by a proper keyword line rather than end-of-file.
    """
    seg_all = seg_facade + seg_drone
    with open(os.path.join(OUT, "blast.inc"), "w") as f:
        f.write("$# battery burst - generated by generate_model.py\n")
        f.write("$# 0.030 kg TNT-equivalent ~ fast-release fraction of a 6S/10Ah LiPo\n")
        f.write("*LOAD_BLAST_ENHANCED\n")
        f.write("$#     bid         m       xbo       ybo       zbo       tbo      unit     blast\n")
        f.write("%10d%10s%10s%10s%10s%10s%10d%10d\n"
                % (1, "0.030", "0.0", "0.0", "0.0", "7.0", 5, 2))
        f.write("$#     cfm       cfl       cft       cfp     nidbo     death   negphs\n")
        f.write("%10s%10s%10s%10s%10d%10s%10d\n"
                % ("1.0", "0.001", "0.001", "1.0E+9", nid_batt, "1.0E+20", 0))
        f.write("$\n")
        f.write("*LOAD_BLAST_SEGMENT_SET\n")
        f.write("$#     bid      ssid     aleid     sfnrb\n")
        f.write("%10d%10d%10d%10.1f\n" % (1, SID_SEG_ALL, 0, 0.0))
        f.write("$\n")
        f.write("$# 903 = building facade (normals face the interior) + drone body\n")
        f.write("$#       inner surface (normals face the charge)\n")
        w_set_segment(f, SID_SEG_ALL, seg_all)
        f.write("$\n")
        f.write("$# 902 = drone body inner surface only, used by the ALTERNATIVE\n")
        f.write("$#       BURST MODEL (*LOAD_SEGMENT_SET) at the bottom of main.k\n")
        w_set_segment(f, SID_SEG_DRONE, seg_drone)
        f.write("$# end blast.inc\n")


# ============================================================================
if __name__ == "__main__":
    b, nbase, seg_facade = build_building()
    d, nbatt, seg_drone = build_drone()
    write_blast(nbatt, seg_facade, seg_drone)
    nsegb, nsegd = len(seg_facade), len(seg_drone)

    def rep(name, m):
        print("%-9s nodes %6d   shells %6d   solids %6d   beams %6d"
              % (name, len(m.nodes), len(m.shells), len(m.solids), len(m.beams)))

    rep("building", b)
    rep("drone", d)
    tot_n = len(b.nodes) + len(d.nodes)
    tot_e = (len(b.shells) + len(b.solids) + len(b.beams) +
             len(d.shells) + len(d.solids) + len(d.beams))
    print("-" * 62)
    print("TOTAL     nodes %6d   elements %6d" % (tot_n, tot_e))
    print("base spc nodes  %6d" % nbase)
    print("facade segments %6d   drone segments %6d" % (nsegb, nsegd))
    print("blast origin node id : %d" % nbatt)
    print("drone centre  (%.0f, %.0f, %.0f) mm, impact velocity %.1f m/s"
          % (DX, DY, DZ, V_IMPACT))
