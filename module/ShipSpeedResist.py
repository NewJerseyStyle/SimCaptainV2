import numpy as np
from scipy.optimize import curve_fit

class Ship:
    def __init__(self, length, displacement, engine_power):
        self.length = length  # 船长(m)
        self.displacement = displacement  # 排水量(t)
        self.engine_power = engine_power  # 发动机功率(kW)

    def calculate_resistance(self, speed):
        # 简化的阻力计算模型
        froude_number = speed / np.sqrt(9.81 * self.length)
        reynolds_number = speed * self.length / (1.19e-6)
        
        cf = 0.075 / (np.log10(reynolds_number) - 2)**2
        cr = 0.0004 * froude_number**4
        
        return 0.5 * 1025 * speed**2 * self.length**2 * (cf + cr)

    def calculate_speed(self, power_percentage):
        # 根据发动机输出百分比计算速度
        available_power = self.engine_power * power_percentage / 100
        
        def power_model(speed):
            return self.calculate_resistance(speed) * speed - available_power

        # 使用二分法求解速度
        low, high = 0, 50  # 假设最高速度为50节
        while high - low > 0.1:
            mid = (low + high) / 2
            if power_model(mid) > 0:
                high = mid
            else:
                low = mid
        return low

    def simulate_speed_range(self):
        speeds = []
        resistances = []
        for power in range(10, 101, 10):  # 从10%到100%的功率
            speed = self.calculate_speed(power)
            resistance = self.calculate_resistance(speed)
            speeds.append(speed)
            resistances.append(resistance)
        return speeds, resistances

    def plot_speed_resistance(self):
        import matplotlib.pyplot as plt
        speeds, resistances = self.simulate_speed_range()
        plt.figure(figsize=(10, 6))
        plt.plot(speeds, resistances, 'b-')
        plt.xlabel('速度 (m/s)')
        plt.ylabel('阻力 (N)')
        plt.title('速度-阻力曲线')
        plt.grid(True)
        plt.show()

# 使用示例
if __name__ == "__main__":
    ship = Ship(length=100, displacement=5000, engine_power=10000)
    ship.plot_speed_resistance()
    print(f"50%功率时的速度: {ship.calculate_speed(50):.2f} m/s")
