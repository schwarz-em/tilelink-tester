import "DPI-C" function void init();

import "DPI-C" function void tick
(
  output          req_valid,
  input           req_ready,
  output longint  req_addr,
  output int      req_data,
  output          req_is_write,
  input           resp_valid,
  input  int      resp_data,
  output          done
);

// TODO: add widths
module TestDriver #(ADDR_BITS=64, DATA_BITS=32) (
  input                 clock,
  input                 reset,
  output                tlt_req_valid,
  input                 tlt_req_ready,
  output [ADDR_BITS:0]  tlt_req_bits_addr,
  output [DATA_BITS:0]  tlt_req_bits_data,
  output                tlt_req_bits_is_write,
  input                 tlt_resp_valid,
  input  [DATA_BITS:0]  tlt_resp_bits_data,
  output                done
);
  
  reg initialized = 1'b0;

  wire __req_ready;
  wire __resp_valid;
  wire [DATA_BITS:0] __resp_data;
  
  bit __req_valid;
  longint __req_addr;
  int __req_data;
  bit __req_is_write;
  bit __done;

  reg __req_valid_reg;
  reg [ADDR_BITS:0] __req_addr;
  reg [DATA_BITS:0] __req_data;
  reg __req_is_write;
  reg __done;

  always @(posedge clock) begin
    if (reset) begin
      __req_valid     = 1'b0;
      __req_addr      = 1'b0;
      __req_data      = 1'b0;
      __req_is_write  = 1'b0;
      __done          = 1'b0;

      __req_valid_reg     <= 1'b0;
      __req_addr_reg      <= 1'b0;
      __req_data_reg      <= 1'b0;
      __req_is_write_reg  <= 1'b0;
      __done_reg          <= 1'b0;
    end else begin
      if (!initialized) begin
        init();
        initialized = 1'b1;
      end
      
      tick(
        __req_valid;
        __req_ready;
        __req_addr;
        __req_data;
        __req_is_write;

        __resp_valid;
        __resp_data;

        __done;
      );

      __req_valid_reg     <= __req_valid;
      __req_addr_reg      <= __req_addr[ADDR_BITS:0];
      __req_data_reg      <= __req_data[DATA_BITS:0];
      __req_is_write_reg  <= __req_is_write;
      __done_reg          <= __done;
    end
  end

  assign  tlt_req_valid = __req_valid_reg;
  assign  tlt_req_bits_addr = __req_addr_reg;
  assign  tlt_req_bits_data = __req_data_reg;
  assign  tlt_req_bits_is_write = __req_is_write;
  assign  done = __done_reg;

endmodule