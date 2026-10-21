#pragma once
#include <aquarium_core.h>

namespace aquarium {
struct Calibration {
    float mvA, valueA, mvB, valueB;
};

inline bool validCalibration(Calibration c, float low, float high, float minMv, float maxMv) {
    return std::isfinite(c.mvA) && std::isfinite(c.mvB) && std::isfinite(c.valueA) && std::isfinite(c.valueB)
        && c.mvA >= minMv && c.mvA <= maxMv && c.mvB >= minMv && c.mvB <= maxMv
        && std::fabs(c.mvB - c.mvA) >= 10 && c.valueA != c.valueB
        && c.valueA >= low && c.valueA <= high && c.valueB >= low && c.valueB <= high;
}

inline float calibrate(float mv, Calibration c, float low, float high, bool clamp = false,
                       float minMv = 150, float maxMv = 3000) {
    if (!validCalibration(c, low, high, minMv, maxMv) || !std::isfinite(mv) || mv < minMv || mv > maxMv) return missing();
    const float value = c.valueA + (mv - c.mvA) * (c.valueB - c.valueA) / (c.mvB - c.mvA);
    if (!std::isfinite(value)) return missing();
    if (clamp) return value < low ? low : value > high ? high : value;
    return validOrMissing(value, low, high);
}

inline float calibratedTemperature(float raw, float offset) {
    if (!std::isfinite(raw) || raw < -55 || raw > 125 || !std::isfinite(offset) || std::fabs(offset) > 5) return missing();
    return validOrMissing(raw + offset, -55, 125);
}

// 15 fresh readings, discard three at each end, average the middle nine.
class AnalogFilter {
public:
    void push(float value, std::uint32_t now) {
        if (!std::isfinite(value)) { count_ = index_ = 0; return; }
        samples_[index_] = value;
        index_ = (index_ + 1) % 15;
        if (count_ < 15) ++count_;
        last_ = now;
    }
    float value(std::uint32_t now) const {
        if (count_ < 15 || elapsed(now, last_, 1000)) return missing();
        float sorted[15];
        for (unsigned i = 0; i < 15; ++i) sorted[i] = samples_[i];
        for (unsigned i = 1; i < 15; ++i) {
            const float value = sorted[i];
            unsigned j = i;
            while (j > 0 && sorted[j - 1] > value) { sorted[j] = sorted[j - 1]; --j; }
            sorted[j] = value;
        }
        float total = 0;
        for (unsigned i = 3; i < 12; ++i) total += sorted[i];
        return total / 9;
    }
private:
    float samples_[15]{};
    unsigned count_ = 0, index_ = 0;
    std::uint32_t last_ = 0;
};

class MotionLight {
public:
    void begin(std::uint32_t now) { started_ = now; lit_ = false; }
    bool update(std::uint32_t now, bool motion, std::uint32_t warmup, std::uint32_t hold) {
        if (!elapsed(now, started_, warmup)) return lit_ = false;
        if (motion) { lastMotion_ = now; lit_ = true; }
        else if (lit_ && elapsed(now, lastMotion_, hold)) lit_ = false;
        return lit_;
    }
private:
    std::uint32_t started_ = 0, lastMotion_ = 0;
    bool lit_ = false;
};
}
