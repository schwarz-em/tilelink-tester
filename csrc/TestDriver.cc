#include <svdpi.h>
#include <stdint.h>

#include "dataset.h"

int req_idx;
int resp_idx;

extern "C" void *init() {
    req_idx = 0;
    resp_idx = 0;
}

//TODO: add reset?
extern "C" void *tick(
    //IO to vlog       
    unsigned char *req_valid,
    unsigned char req_ready,
    long long int *req_addr,
    long int *req_data,
    unsigned char *req_is_write,

    unsigned char resp_valid,
    long int resp_data,

    unsigned char *done
) {

    // Should never recieve more responses than number of sent requests
    assert(resp_idx <= req_idx);

    bool req_fire = req_valid && req_ready

    if (req_fire) {
        req_idx = req_idx + 1;
    }

    if (resp_valid) {
        if (req_types[resp_idx]) { //If outstanding request was a write
            assert(resp_data == data_array[resp_idx]);
        }
        resp_idx = resp_idx + 1;
    }

    // Send next request
    *req_valid = req_idx < NUM_REQS;
    if (req_idx < NUM_REQS) {
        *req_addr = addr_array[req_idx];
        *req_data = data_array[req_idx];
        *req_is_write = req_types[req_idx];
    }

    *done = (resp_idx == (NUM_REQS - 1));

    return;
}