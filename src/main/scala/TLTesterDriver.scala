package tlt

import chisel3._
import chisel3.experimental.IntParam
import chisel3.util.HasBlackBoxResource
import org.chipsalliance.cde.config.Parameters

class TLTesterDriver(addrWidth: Int, dataWidth: Int, idBits: Int, maxInflight: Int)(implicit p: Parameters) extends BlackBox(Map(
                  "ADDR_BITS" -> IntParam(addrWidth),
                  "DATA_BITS" -> IntParam(dataWidth),
                  "ID_BITS" -> IntParam(idBits),
                  "MAX_INFLIGHT" -> IntParam(maxInflight)
                  )) with HasBlackBoxResource {
  val io = IO(new Bundle {
    val clock = Input(Clock())
    val reset = Input(Reset())
    val tlt = Flipped(new TesterIO)
    val done = Output(Bool())
  })

  addResource("/tilelink-tester/vsrc/TLTesterDriver.v")
  addResource("/tilelink-tester/csrc/TLTesterDriver.cc")
}
