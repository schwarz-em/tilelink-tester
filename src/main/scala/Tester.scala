package tlt

// FIXME: clean up imports
import chisel3._
import chisel3.util._
//import freechips.rocketchip.diplomacy._
import freechips.rocketchip.tilelink._
//import org.chipsalliance.cde.config.Parameters
//import freechips.rocketchip.util._
//import freechips.rocketchip.prci._
//import freechips.rocketchip.subsystem._

class TesterParams {
  val placeholder
}

// TODO: set widths
class TesterReq extends Bundle() {
  val addr = Output(UInt())
  val data = Output(UInt())
  val is_write = Output(Bool())
}

class TesterResp {
  val data = Output(UInt())
}

class TesterIO extends Bundle() {
  val req = Flipped(new DecoupledIO(new TesterReq))
  val resp = ValidIO(new TesterResp)
}

class TileLinkTester()(implicit p: Parameters) extends LazyModule {

  val node = TLClientNode(Seq(TLMasterPortParameters.v1(
    clients = Seq(TLMasterParameters.v1(
    name = "tester-node",
    sourceId = IdRange(0, maxInflight) //FIXME
    ))
  )))
    
  lazy val module = new TileLinkTesterModuleImp(this)
}

class TileLinkTesterModuleImp(outer: TileLinkTester) extends LazyModuleImp(outer) {
  val io = IO(new TesterIO)

  val (out, edge) = outer.node.out(0)
  val beatBytes = 8.U

  io.req.ready := out.a.ready
  out.d.ready := true.B

  out.a.valid := io.req.valid
  out.a.bits := Mux(io.req.bits.is_write, 
                  edge.Get(0.U, io.req.bits.addr, beatBytes)
                  edge.Put(0.U, io.req.bits.addr, beatBytes, io.req.bits.data))

  //  Bug (maybe?): make sure to check that d opcode was access ack data (ie resp to read)
  // JK this actually might be helpful
  io.resp.valid := out.d.valid
  io.resp.bits.data := out.d.bits.data

}