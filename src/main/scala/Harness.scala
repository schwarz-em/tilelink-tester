package tlt

import chisel3._
import chisel3.util._

import freechips.rocketchip.diplomacy._
import org.chipsalliance.cde.config.{Field, Parameters, Config}
import freechips.rocketchip.tilelink._
import freechips.rocketchip.util._
import freechips.rocketchip.prci._

trait HasTesterSuccessIO { this: Module =>
  val io = IO(new Bundle {
    val success = Output(Bool())
  })
}

class TesterDebug(implicit p: Parameters) extends LazyModule {
  val testerParams = p(TesterParamsKey)

  val tltester = LazyModule(new TileLinkTester)

  val mem = LazyModule(new TLRAM(AddressSet(BigInt(0x100000000L), BigInt(0x0FFFFL))))

  mem.node := tltester.node

  lazy val module = new Impl
  class Impl extends LazyModuleImp(this) {
    val io = IO(new Bundle {
      val done = Output(Bool())
    })

    val driver = Module(new TLTesterDriver(testerParams.addrWidth, testerParams.dataWidth, log2Up(testerParams.maxInflight), testerParams.maxInflight)) 

    driver.io.tlt <> tltester.module.io
    driver.io.clock := clock
    driver.io.reset := reset

    io.done := driver.io.done
  }
}

class TesterDebugHarness(implicit val p: Parameters) extends Module with HasTesterSuccessIO {
  val tester = Module(LazyModule(new TesterDebug).module)
  io.success := tester.io.done
}


