/* verilator lint_off DECLFILENAME */

module top (
	input wire clk,
	input wire [1:0] addr,
	output wire [7:0] rdata
);
	rom dut (
		.clk(clk),
		.addr(addr),
		.rdata(rdata)
	);

	initial begin
		$display("Hello!");
		$display($test$plusargs("HELLO"));
		$readmemh("rom.hex", dut.arr);
	end
endmodule

module rom (
	input  wire       clk,
	input  wire [1:0] addr,
	output reg  [7:0] rdata
);

reg [7:0] arr [3:0];

always @(posedge clk) begin
	rdata <= arr[addr];
end

endmodule
