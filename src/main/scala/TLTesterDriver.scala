package tlt

import chisel3._
import chisel3.experimental.IntParam
import chisel3.util.HasBlackBoxResource

// TODO: fix scala so that testdriver and tester always have the same params
class TLTesterDriver(params: TesterParams) extends BlackBox(Map(
                  "ADDR_BITS" -> IntParam(params.addrWidth),
                  "DATA_BITS" -> IntParam(params.dataWidth)
                  )) with HasBlackBoxResource {
  val io = IO(new Bundle {
    val clock = Input(Clock())
    val reset = Input(Reset())
    val tlt = Flipped(new TesterIO(params.addrWidth, params.dataWidth))
    val done = Output(Bool())
  })

  addResource("/tilelink-tester/vsrc/TLTesterDriver.v")
  addResource("/tilelink-tester/csrc/TLTesterDriver.cc")
  addResource("/tilelink-tester/csrc/dataset.h")
}