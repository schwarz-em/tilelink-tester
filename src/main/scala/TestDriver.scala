package tlt

import chisel3._
import chisel3.util.HasBlackBoxResource

class TestDriver() extends BlackBox {
  val io = IO(new Bundle {
    val clock = Input(Clock())
    val reset = Input(Reset())
    val tlt = Flipped(new TesterIO)
    val done = Output(Bool())
  })

  addResource("tilelink-tester/vsrc/TestDriver.v")
  addResource("tilelink-tester/vsrc/TestDriver.cc")
}