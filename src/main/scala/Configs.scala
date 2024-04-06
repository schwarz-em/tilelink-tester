package tlt

import chisel3._
import chisel3.util._

import org.chipsalliance.cde.config.{Field, Parameters, Config}

class TLTesterConfig(p: TesterParams) extends Config((site, here, up) => {
  case TesterParamsKey => p
})

class DebugTLTConfig0 extends TLTesterConfig(
    new TesterParams(maxInflight=4, beatBytes=4)
)

class DebugTLTConfig1 extends TLTesterConfig(
    new TesterParams(maxInflight=1, beatBytes=4)
)

class TLTConfig(maxInflight: Int, beatBytes: Int) extends TLTesterConfig(
  new TesterParams(maxInflight=maxInflight, beatBytes=beatBytes)
)