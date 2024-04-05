package tlt

import chisel3._
import chisel3.util._

import org.chipsalliance.cde.config.{Field, Parameters, Config}

class TLTesterConfig(p: TesterParams) extends Config((site, here, up) => {
  case TesterParamsKey => p
})

class DebugTLTConfig extends TLTesterConfig(
    new TesterParams(beatBytes=4)
)