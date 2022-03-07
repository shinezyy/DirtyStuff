#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cstdint>
#include <cassert>
#include <vector>

using namespace std;

int main() {
	vector<uint64_t> m;
	char *name;
	int width;
	int depth;
	int mask;
	// nreader,nwriter,nreadwriter

	char *line = NULL;
	size_t bufSize = 0;
	size_t bytesRead = 0;

	size_t addr;
	char *en;
	char *wmode;
	uint64_t wdata;
	uint64_t rdata;
	uint64_t lastRdata;
	bool lastRen = false;

	unsigned int lineno = 0;
	while ((bytesRead = getline(&line, &bufSize, stdin)) != EOF) {
		lineno++;

		switch (lineno) {
		case 1: // config header
			break;
		case 2:	// config
			name = strdup(strtok(line, ","));
			printf(">%s< ", name);
			width = atoi(strtok(NULL, ","));
			printf("w=%d ", width);
			depth = atoi(strtok(NULL, ","));
			printf("d=%d\n", depth);
			m.resize(depth);
			break;
		case 3:	// data header
			break;
		default: // data
			addr = strtoul(strtok(line, ","), NULL, 2);
			en = strtok(NULL, ",");
			// read verification
			assert(!lastRen || lastRdata == rdata);
			if (*en == '1') {
				wmode = strtok(NULL, ",");
				wdata = strtoul(strtok(NULL, ","), NULL, 2);
				rdata = strtoul(strtok(NULL, ","), NULL, 2);
				if (*wmode == '1') { // write
					m[addr] = wdata;
				} else { // read verification
					lastRen = true;
					lastRdata = m[addr];
				}
			}
			lastRen = false;
		}
	}

	char *file;
	asprintf(&file, "build/trace/%s.hex", name);
	free(name);
	FILE *o = fopen(file, "w");
	free(file);

	for (auto d : m) {
		/* // bin
		for (auto i = width - 1; i >= 0; i--) {
			printf("%c", (d & (1 << i)) == 0 ? '0' : '1');
		}
		printf("\n");
		*/

		// hex
		char *fmt;
		asprintf(&fmt, "%%0%dlX\n", (width + 3) / 4);
		fprintf(o, fmt, d);
		free(fmt);
	}
	return 0;
}

