import { useState, useEffect, useCallback } from 'react';
import { getSDK } from '../services/auth-service';
import { handleError } from '../utils/error-handler';
import {
  ABTestResponse,
  ABTestUpdateRequest,
  ABTestCreateRequest,
  ABTestMetricsResponse,
  ABTestResultsResponse,
} from 'chatter-sdk';

export type TestStatus =
  | 'draft'
  | 'running'
  | 'paused'
  | 'completed'
  | 'cancelled';

export interface TestRecommendations {
  recommendations: string[];
  insights: string[];
  winner?: string;
  confidence?: number;
}

export interface TestPerformance {
  response_times: Array<{
    timestamp: string;
    variant: string;
    response_time: number;
  }>;
  error_rates: Array<{
    timestamp: string;
    variant: string;
    error_rate: number;
  }>;
  throughput: Array<{
    timestamp: string;
    variant: string;
    requests_per_second: number;
  }>;
}

export const useABTestingData = () => {
  const [tests, setTests] = useState<ABTestResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedTest, setSelectedTest] = useState<ABTestResponse | null>(null);

  // Test metrics and analysis data
  const [testMetrics, setTestMetrics] = useState<ABTestMetricsResponse | null>(
    null
  );
  const [testResults, setTestResults] = useState<ABTestResultsResponse | null>(
    null
  );
  const [testPerformance, setTestPerformance] =
    useState<TestPerformance | null>(null);
  const [testRecommendations, setTestRecommendations] =
    useState<TestRecommendations | null>(null);

  const loadTests = useCallback(async () => {
    try {
      setLoading(true);
      const response = await getSDK().abTesting.listAbTestsApiV1AbTests();
      setTests(response.tests || []);
    } catch (error) {
      handleError(error, {
        source: 'useABTestingData.loadTests',
        operation: 'load AB tests',
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const loadTestDetails = useCallback(async (testId: string) => {
    try {
      const [metricsResp, resultsResp, performanceResp, recommendationsResp] =
        await Promise.allSettled([
          getSDK().abTesting.getAbTestMetricsApiV1AbTestsTestIdMetrics(testId),
          getSDK().abTesting.getAbTestResultsApiV1AbTestsTestIdResults(testId),
          getSDK().abTesting.getAbTestPerformanceApiV1AbTestsTestIdPerformance(
            testId
          ),
          getSDK().abTesting.getAbTestRecommendationsApiV1AbTestsTestIdRecommendations(
            testId
          ),
        ]);

      // Handle metrics
      if (metricsResp.status === 'fulfilled') {
        setTestMetrics(metricsResp.value);
      } else {
        setTestMetrics(null);
      }

      // Handle results
      if (resultsResp.status === 'fulfilled') {
        setTestResults(resultsResp.value);
      } else {
        setTestResults(null);
      }

      // Handle performance
      if (performanceResp.status === 'fulfilled') {
        setTestPerformance(performanceResp.value as unknown as TestPerformance);
      } else {
        setTestPerformance(null);
      }

      // Handle recommendations
      if (recommendationsResp.status === 'fulfilled') {
        setTestRecommendations(
          recommendationsResp.value as unknown as TestRecommendations
        );
      } else {
        setTestRecommendations(null);
      }
    } catch (error) {
      handleError(error, {
        source: 'useABTestingData.loadTestDetails',
        operation: 'load test details',
      });
    }
  }, []);

  const createTest = useCallback(async (testData: ABTestCreateRequest) => {
    try {
      setSaving(true);
      const newTest =
        await getSDK().abTesting.createAbTestApiV1AbTests(testData);
      setTests((prev) => [newTest, ...prev]);
      return newTest;
    } catch (error) {
      handleError(error, {
        source: 'useABTestingData.createTest',
        operation: 'create AB test',
      });
      throw error;
    } finally {
      setSaving(false);
    }
  }, []);

  const updateTest = useCallback(
    async (testId: string, testData: ABTestUpdateRequest) => {
      try {
        setSaving(true);
        const updatedTest =
          await getSDK().abTesting.updateAbTestApiV1AbTestsTestId(
            testId,
            testData
          );
        setTests((prev) =>
          prev.map((test) => (test.id === testId ? updatedTest : test))
        );
        if (selectedTest?.id === testId) {
          setSelectedTest(updatedTest);
        }
        return updatedTest;
      } catch (error) {
        handleError(error, {
          source: 'useABTestingData.updateTest',
          operation: 'update AB test',
        });
        throw error;
      } finally {
        setSaving(false);
      }
    },
    [selectedTest]
  );

  const deleteTest = useCallback(
    async (testId: string) => {
      try {
        setSaving(true);
        await getSDK().abTesting.deleteAbTestApiV1AbTestsTestId(testId);
        setTests((prev) => prev.filter((test) => test.id !== testId));
        if (selectedTest?.id === testId) {
          setSelectedTest(null);
        }
      } catch (error) {
        handleError(error, {
          source: 'useABTestingData.deleteTest',
          operation: 'delete AB test',
        });
        throw error;
      } finally {
        setSaving(false);
      }
    },
    [selectedTest]
  );

  const startTest = useCallback(
    async (testId: string) => {
      try {
        await getSDK().abTesting.startAbTestApiV1AbTestsTestIdStart(testId);
        await loadTests(); // Reload to get updated status
      } catch (error) {
        handleError(error, {
          source: 'useABTestingData.startTest',
          operation: 'start AB test',
        });
      }
    },
    [loadTests]
  );

  const stopTest = useCallback(
    async (testId: string) => {
      try {
        await getSDK().abTesting.pauseAbTestApiV1AbTestsTestIdPause(testId);
        await loadTests(); // Reload to get updated status
      } catch (error) {
        handleError(error, {
          source: 'useABTestingData.stopTest',
          operation: 'stop AB test',
        });
      }
    },
    [loadTests]
  );

  // Load tests on mount
  useEffect(() => {
    loadTests();
  }, [loadTests]);

  // Load test details when selected test changes
  useEffect(() => {
    if (selectedTest?.id) {
      loadTestDetails(selectedTest.id);
    } else {
      setTestMetrics(null);
      setTestResults(null);
      setTestPerformance(null);
      setTestRecommendations(null);
    }
  }, [selectedTest?.id, loadTestDetails]);

  return {
    // Data
    tests,
    loading,
    saving,
    selectedTest,
    testMetrics,
    testResults,
    testPerformance,
    testRecommendations,

    // Actions
    setSelectedTest,
    loadTests,
    loadTestDetails,
    createTest,
    updateTest,
    deleteTest,
    startTest,
    stopTest,
  };
};
