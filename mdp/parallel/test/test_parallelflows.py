
import unittest

import mdp
import mdp.parallel as parallel
n = mdp.numx


class TestParallelFlows(unittest.TestCase):

    def test_jobs(self):
        """Test parallel training and execution by running the jobs."""
        flow = parallel.ParallelFlow([
                            parallel.ParallelSFANode(output_dim=5),
                            mdp.nodes.PolynomialExpansionNode(degree=3),
                            parallel.ParallelSFANode(output_dim=20)])
        data_generators = [n.random.random((6,20,10)), 
                           None, 
                           n.random.random((6,20,10))]
        flow.parallel_train(data_generators)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
        # test execution
        x = n.random.random([100,10])
        flow.execute(x)
        # parallel execution
        data = [n.random.random((20,10)) for _ in range(6)]
        flow.parallel_execute(data)
        results = []
        while flow.job_available():
            job = flow.get_job()
            results.append(job())
        flow.use_results(results)
        
    def test_multiphase(self):
        """Test parallel training and execution for nodes with multiple
        training phases.
        """
        sfa_node = parallel.ParallelSFANode(input_dim=10, output_dim=8)
        sfa2_node = parallel.ParallelSFA2Node(input_dim=8, output_dim=6)
        flownode = parallel.ParallelFlowNode(mdp.Flow([sfa_node, sfa2_node]))
        flow = parallel.ParallelFlow([
                            flownode,
                            mdp.nodes.PolynomialExpansionNode(degree=2),
                            parallel.ParallelSFANode(output_dim=5)])
        data_generators = [n.random.random((6,30,10)), 
                           None, 
                           n.random.random((6,30,10))]
        flow.parallel_train(data_generators)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
        # test execution
        x = n.random.random([100,10])
        flow.execute(x)
        # parallel execution
        data = [n.random.random((20,10)) for _ in range(6)]
        flow.parallel_execute(data)
        results = []
        while flow.job_available():
            job = flow.get_job()
            results.append(job())
        flow.use_results(results)
        
    def test_firstnode(self):
        """Test special case in which the first node is untrainable.
        
        This tests the proper initialization of the internal variables.
        """
        flow = parallel.ParallelFlow([
                            mdp.nodes.PolynomialExpansionNode(degree=2),
                            parallel.ParallelSFANode(output_dim=20)])
        data_generators = [None, 
                           n.random.random((6,20,10))]
        flow.parallel_train(data_generators)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
            
    def test_multiphase_checkpoints(self):
        """Test parallel checkpoint flow."""
        sfa_node = parallel.ParallelSFANode(input_dim=10, output_dim=8)
        sfa2_node = parallel.ParallelSFA2Node(input_dim=8, output_dim=6)
        flownode = parallel.ParallelFlowNode(mdp.Flow([sfa_node, sfa2_node]))
        flow = parallel.ParallelCheckpointFlow([
                            flownode,
                            mdp.nodes.PolynomialExpansionNode(degree=2),
                            parallel.ParallelSFANode(output_dim=5)])
        data_generators = [n.random.random((6,30,10)), 
                           None, 
                           n.random.random((6,30,10))]
        checkpoint = mdp.CheckpointFunction()
        flow.parallel_train(data_generators, checkpoints=checkpoint)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
            
    def test_nonparallel1(self):
        """Test training for mixture of parallel and non-parallel nodes."""
        sfa_node = parallel.ParallelSFANode(input_dim=10, output_dim=8)
        sfa2_node = mdp.nodes.SFA2Node(input_dim=8, output_dim=6)
        flownode = parallel.ParallelFlowNode(mdp.Flow([sfa_node, sfa2_node]))
        flow = parallel.ParallelFlow([
                            flownode,
                            mdp.nodes.PolynomialExpansionNode(degree=2),
                            parallel.ParallelSFANode(output_dim=5)])
        data_generators = [n.random.random((6,30,10)), 
                           None, 
                           n.random.random((6,30,10))]
        flow.parallel_train(data_generators)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
        # test execution
        x = n.random.random([100,10])
        flow.execute(x)
        
    def test_nonparallel2(self):
        """Test training for mixture of parallel and non-parallel nodes."""
        sfa_node = mdp.nodes.SFANode(input_dim=10, output_dim=8)
        sfa2_node = parallel.ParallelSFA2Node(input_dim=8, output_dim=6)
        flownode = parallel.ParallelFlowNode(mdp.Flow([sfa_node, sfa2_node]))
        flow = parallel.ParallelFlow([
                            flownode,
                            mdp.nodes.PolynomialExpansionNode(degree=2),
                            parallel.ParallelSFANode(output_dim=5)])
        data_generators = [n.random.random((6,30,10)), 
                           None, 
                           n.random.random((6,30,10))]
        flow.parallel_train(data_generators)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
        # test execution
        x = n.random.random([100,10])
        flow.execute(x)
        
    def test_nonparallel3(self):
        """Test training for non-parallel nodes."""
        sfa_node = mdp.nodes.SFANode(input_dim=10, output_dim=8)
        sfa2_node = mdp.nodes.SFA2Node(input_dim=8, output_dim=6)
        flow = parallel.ParallelFlow([sfa_node, sfa2_node])
        data_generators = [n.random.random((6,30,10)), 
                           n.random.random((6,30,10))]
        flow.parallel_train(data_generators)
        while flow.is_parallel_training():
            results = []
            while flow.job_available():
                job = flow.get_job()
                results.append(job())
            flow.use_results(results)
        # test execution
        x = n.random.random([100,10])
        flow.execute(x)

    
def get_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParallelFlows))
    return suite
            
if __name__ == '__main__':
    unittest.main() 