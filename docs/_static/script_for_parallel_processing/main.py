import ciw
import multiprocessing

N = ciw.create_network(
    arrival_distributions=[ciw.dists.Exponential(rate=0.2)],
    service_distributions=[ciw.dists.Exponential(rate=0.1)],
    number_of_servers=[3],
)

max_time = 500
repetitions = 200


def get_mean_wait(network, seed=0, max_time=10000):
    """Return the mean waiting time for a given network"""
    ciw.seed(seed)
    Q = ciw.Simulation(network)
    Q.simulate_until_max_time(max_simulation_time=max_time)
    recs = Q.get_all_records()
    waits = [r.waiting_time for r in recs]
    mean_wait = sum(waits) / len(waits)
    return mean_wait


if __name__ == "__main__":
    pool = multiprocessing.Pool(processes=2)
    args = [(N, seed, max_time) for seed in range(repetitions)]
    waits = pool.starmap(get_mean_wait, args)
    print(sum(waits) / repetitions)
