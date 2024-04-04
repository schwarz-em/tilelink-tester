package tlt

// FIXME: clean up imports
import chisel3._
import chisel3.util._
import freechips.rocketchip.diplomacy._
import freechips.rocketchip.tilelink._
import org.chipsalliance.cde.config.Parameters
//import freechips.rocketchip.util._
//import freechips.rocketchip.prci._
//import freechips.rocketchip.subsystem._

case class TesterParams (
  maxInflight: Int = 1,
  addrWidth: Int = 64,
  dataWidth: Int = 32,
  beatBytes: Int
) {
  def lgBeatBytes = log2Ceil(beatBytes)
}

class TesterReq(addrWidth: Int, dataWidth: Int) extends Bundle {
  val addr = Output(UInt(addrWidth.W))
  val data = Output(UInt(dataWidth.W))
  val is_write = Output(Bool())
}

class TesterResp(dataWidth: Int) extends Bundle {
  val data = Output(UInt(dataWidth.W))
}

class TesterIO(addrWidth: Int, dataWidth: Int) extends Bundle {
  val req = Flipped(new DecoupledIO(new TesterReq(addrWidth, dataWidth)))
  val resp = new ValidIO(new TesterResp(dataWidth))
}

class TileLinkTester(pparams: TesterParams)(implicit p: Parameters) extends LazyModule {

  val params = pparams

  val node = TLClientNode(Seq(TLMasterPortParameters.v1(
    clients = Seq(TLMasterParameters.v1(
    name = "tester-node",
    sourceId = IdRange(0, params.maxInflight) 
    ))
  )))
    
  lazy val module = new TileLinkTesterModuleImp(this)
}

class TileLinkTesterModuleImp(outer: TileLinkTester) extends LazyModuleImp(outer) {
  val io = IO(new TesterIO(outer.params.addrWidth, outer.params.dataWidth))

  val (out, edge) = outer.node.out(0)
  //val beatBytes = 5.U //32.U // FIXME: don't hardcode

  io.req.ready := out.a.ready
  out.d.ready := true.B

  out.a.valid := io.req.valid
  // First arg is the source id
  out.a.bits := Mux(io.req.bits.is_write, 
                  edge.Put(0.U, io.req.bits.addr, outer.params.lgBeatBytes.U, io.req.bits.data)._2,
                  edge.Get(0.U, io.req.bits.addr, outer.params.lgBeatBytes.U)._2)

  io.resp.valid := out.d.valid
  io.resp.bits.data := out.d.bits.data

}