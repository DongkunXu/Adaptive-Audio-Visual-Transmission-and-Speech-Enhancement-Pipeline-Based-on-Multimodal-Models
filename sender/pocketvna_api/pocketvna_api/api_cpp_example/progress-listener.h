#pragma once
#include <functional>
#include <pocketvna.h>

using ProgressCallback = std::function<bool(size_t)>;
///> Functor that could be passed to pocketvna_multi_query to track progress
/// allows passing lambdas/functions/functors into API
struct ProgressListener {
    ProgressCallback proc;


    PVNA_ContinueCode operator()(size_t i) const {
        return proc(i) ? PVNA_Continue : PVNA_Cancel;
    }

    static PVNA_ContinueCode listener(PVNA_UserDataPtr data, uint32_t count) {
        ProgressListener & l = *(reinterpret_cast<ProgressListener*>(data));
        return l(count);
    }

    PVNA_ProgressCallBack toProc() {
        return {
            reinterpret_cast<PVNA_UserDataPtr>(this),
            listener
        };
    }
};
