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

  //val testerParams = TesterParams(beatBytes=4*1)
  val testerParams = p(TesterParamsKey)

  val tltester = LazyModule(new TileLinkTester)

  val bb = 32
  // val node = TLManagerNode(Seq(TLSlavePortParameters.v1(
  //   Seq(TLSlaveParameters.v1(
  //     address = Seq(AddressSet(BigInt(0x100000000L), BigInt(0x0FFFFL))),
  //     regionType = RegionType.UNCACHED,
  //     executable = true,
  //     supportsGet = TransferSizes(beatBytes, beatBytes), //change back to 1,beatBytes for chipyard 
  //     supportsPutFull = TransferSizes(beatBytes, beatBytes), //change back to 1,beatBytes for chipyard 
  //     supportsPutPartial = TransferSizes(beatBytes, beatBytes), //change back to 1,beatBytes for chipyard 
  //     fifoId = Some(0))), 
  //   beatBytes = beatBytes)))

  val mem = LazyModule(new TLRAM(AddressSet(BigInt(0x100000000L), BigInt(0x0FFFFL))))

  mem.node := tltester.node

  lazy val module = new Impl
  class Impl extends LazyModuleImp(this) {
    val io = IO(new Bundle {
      val done = Output(Bool())
    })

    // val (in, edge) = node.in(0)
    // in.a.ready := true.B
    // in.d.valid := false.B

    val driver = Module(new TLTesterDriver(testerParams.addrWidth, testerParams.dataWidth, log2Up(testerParams.maxInflight), testerParams.maxInflight)) //ew
    //val driver = Module(new TLTesterDriver(testerParams.addrWidth, testerParams.dataWidth, 32, testerParams.maxInflight)) //ew

    driver.io.tlt <> tltester.module.io
    driver.io.clock := clock
    driver.io.reset := reset

    io.done := driver.io.done
  }
}

class TesterDebugHarness(implicit val p: Parameters) extends Module with HasTesterSuccessIO {
  val tester = Module(LazyModule(new TesterDebug).module)
  io.success := tester.io.done

  // Dummy plusarg to avoid breaking verilator builds with emulator.cc
  val useless_plusarg = PlusArg("useless_plusarg", width=1)
  dontTouch(useless_plusarg)
  ElaborationArtefacts.add("plusArgs", PlusArgArtefacts.serialize_cHeader)
}


