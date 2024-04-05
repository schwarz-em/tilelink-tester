import "DPI-C" function void init(
  input int max_inflight
);

import "DPI-C" function void tick
(
  output longint unsigned req_valid,
  input                   req_ready,
  output longint unsigned req_addr,
  output longint unsigned req_data,
  output longint unsigned req_id,
  output longint unsigned req_is_write,
  input                   resp_valid,
  input  int              resp_data,
  input  int              resp_id,
  output longint unsigned done
);

// TODO: add widths
module TLTesterDriver #(ADDR_BITS, DATA_BITS, ID_BITS, MAX_INFLIGHT) (
  input                   clock,
  input                   reset,
  output                  tlt_req_valid,
  input                   tlt_req_ready,
  output [ADDR_BITS-1:0]  tlt_req_bits_addr,
  output [DATA_BITS-1:0]  tlt_req_bits_data,
  output [ID_BITS-1:0]    tlt_req_bits_id,
  output                  tlt_req_bits_is_write,
  input                   tlt_resp_valid,
  input  [DATA_BITS-1:0]  tlt_resp_bits_data,
  input  [ID_BITS-1:0]    tlt_resp_bits_id,
  output                  done
);
  
  reg initialized = 1'b0;

  wire __req_ready;
  wire __resp_valid;
  wire [DATA_BITS-1:0] __resp_data;
  wire [ID_BITS-1:0] __resp_id;
  
  bit __req_valid;
  longint __req_addr;
  int __req_data;
  int __req_id;
  bit __req_is_write;
  bit __done;

  reg __req_valid_reg;
  reg [ADDR_BITS-1:0] __req_addr_reg;
  reg [DATA_BITS-1:0] __req_data_reg;
  reg [ID_BITS-1:0] __req_id_reg;
  reg __req_is_write_reg;
  reg __done_reg;

  always @(posedge clock) begin
    if (reset) begin
      __req_valid     = 1'b0;
      __req_addr      = 1'b0;
      __req_data      = 1'b0;
      __req_id        = 1'b0;
      __req_is_write  = 1'b0;
      __done          = 1'b0;

      __req_valid_reg     <= 1'b0;
      __req_addr_reg      <= 1'b0;
      __req_data_reg      <= 1'b0;
      __req_id_reg        <= 1'b0;
      __req_is_write_reg  <= 1'b0;
      __done_reg          <= 1'b0;
    end else begin
      if (!initialized) begin
        init(MAX_INFLIGHT);
        initialized = 1'b1;
      end
      
      tick(
        __req_valid,
        __req_ready,
        __req_addr,
        __req_data,
        __req_id,
        __req_is_write,

        __resp_valid,
        __resp_data,
        __resp_id,

        __done);

      __req_valid_reg     <= __req_valid;
      __req_addr_reg      <= __req_addr[ADDR_BITS-1:0];
      __req_data_reg      <= __req_data[DATA_BITS-1:0];
      __req_id_reg        <= __req_id[ID_BITS-1:0];
      __req_is_write_reg  <= __req_is_write;
      __done_reg          <= __done;
    end
  end

  assign __req_ready = tlt_req_ready;
  assign __resp_valid = tlt_resp_valid;
  assign __resp_data = tlt_resp_bits_data;
  assign __resp_id = tlt_resp_bits_id;

  assign  tlt_req_valid = __req_valid_reg;
  assign  tlt_req_bits_addr = __req_addr_reg;
  assign  tlt_req_bits_data = __req_data_reg;
  assign  tlt_req_bits_id = __req_id_reg;
  assign  tlt_req_bits_is_write = __req_is_write_reg;
  assign  done = __done_reg;

endmodule