package tlt

// FIXME: clean up imports
import chisel3._
import chisel3.util._
import freechips.rocketchip.diplomacy._
import freechips.rocketchip.tilelink._
import org.chipsalliance.cde.config.{Parameters, Field}
import freechips.rocketchip.util._
//import freechips.rocketchip.prci._
//import freechips.rocketchip.subsystem._

case object TesterParamsKey extends Field[TesterParams]

trait HasTesterParams {
  implicit val p: Parameters
  def tParams: TesterParams = p(TesterParamsKey)

  def lgBeatBytes = log2Up(tParams.beatBytes)
  def idBits = log2Up(tParams.maxInflight)
}

case class TesterParams (
  maxInflight: Int = 4,
  addrWidth: Int = 64,
  dataWidth: Int = 32,
  beatBytes: Int
)

abstract class TesterBundle(implicit val p: Parameters) extends ParameterizedBundle()(p) with HasTesterParams

// TODO: pass in tester params, this is bad scala
class TesterReq(implicit p: Parameters) extends TesterBundle {
  val addr = Output(UInt(tParams.addrWidth.W))
  val data = Output(UInt(tParams.dataWidth.W))
  val id = Output(UInt(idBits.W))
  val is_write = Output(Bool())
}

class TesterResp(implicit p: Parameters) extends TesterBundle {
  val data = Output(UInt(tParams.dataWidth.W))
  val id = Output(UInt(idBits.W))
}

class TesterIO(implicit p: Parameters) extends TesterBundle { //does this need params?
  val req = Flipped(new DecoupledIO(new TesterReq))
  val resp = new ValidIO(new TesterResp)
}

class TileLinkTester(implicit p: Parameters) extends LazyModule with HasTesterParams {

  val node = TLClientNode(Seq(TLMasterPortParameters.v1(
    clients = Seq(TLMasterParameters.v1(
    name = "tester-node",
    sourceId = IdRange(0, tParams.maxInflight) 
    ))
  )))
    
  lazy val module = new Impl // TileLinkTesterModuleImp(this)
  class Impl extends LazyModuleImp(this) {
    val io = IO(new TesterIO)

    val (out, edge) = node.out(0)
    //val beatBytes = 5.U //32.U // FIXME: don't hardcode

    io.req.ready := out.a.ready
    out.d.ready := true.B

    out.a.valid := io.req.valid
    // First arg is the source id
    out.a.bits := Mux(io.req.bits.is_write, 
                    edge.Put(io.req.bits.id, io.req.bits.addr, lgBeatBytes.U, io.req.bits.data)._2,
                    edge.Get(io.req.bits.id, io.req.bits.addr, lgBeatBytes.U)._2)

    io.resp.valid     := out.d.valid
    io.resp.bits.data := out.d.bits.data
    io.resp.bits.id   := out.d.bits.source
  }
}