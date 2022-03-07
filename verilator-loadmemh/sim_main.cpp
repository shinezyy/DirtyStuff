#include "Vtop.h"
#include "verilated.h"
#include <cassert>

int main(int argc, char** argv, char** env) {
	VerilatedContext* contextp = new VerilatedContext;
	contextp->commandArgs(argc, argv);
	Vtop* top = new Vtop{contextp};
	top->clk = 0;
	int cycle = 10;
	while (cycle--) {
		top->addr = cycle & 3;
		printf("0x%02X, 0x%02X\n", top->addr, top->rdata);

		top->clk = 1;
		top->eval();
		top->clk = 0;
		top->eval();
	}
	delete top;
	delete contextp;
	return 0;
}
