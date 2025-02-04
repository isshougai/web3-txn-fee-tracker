import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Container, TextField, Button, Table, TableHead, TableRow, TableCell, TableBody, TablePagination, Typography, Box, CircularProgress, Chip, Paper } from "@mui/material";
import qs from 'qs';

const TransactionTracker = () => {
  const [txId, setTxId] = useState("");
  const [txHashes, setTxHashes] = useState([]);
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [transactions, setTransactions] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);
  const [summary, setSummary] = useState({ totalUsdt: 0, totalEth: 0, ethPrice: 0 });
  const [loading, setLoading] = useState(false);

  const handleTxIdChange = (e) => {
    const value = e.target.value;
    if (value.includes(",")) {
      const newHashes = value.split(",").map(hash => hash.trim()).filter(hash => hash);
      setTxHashes([...txHashes, ...newHashes]);
      setTxId("");
    } else {
      setTxId(value);
    }
  };

  const handleTxIdBlur = () => {
    if (txId.trim()) {
      setTxHashes([...txHashes, txId.trim()]);
      setTxId("");
    }
  };

  const handleTxIdKeyPress = (e) => {
    if (e.key === "Enter" && txId.trim()) {
      setTxHashes([...txHashes, txId.trim()]);
      setTxId("");
    }
  };

  const handleDeleteTxHash = (hashToDelete) => {
    setTxHashes(txHashes.filter(hash => hash !== hashToDelete));
  };

  const fetchTransactions = useCallback(async () => {
    setLoading(true);
    try {
      const params = {
        tx_hashes: txHashes.length > 0 ? txHashes : undefined,
        start_time: startTime ? new Date(startTime).getTime() : undefined,
        end_time: endTime ? new Date(endTime).getTime() : undefined,
        skip: page * rowsPerPage,
        limit: rowsPerPage,
      };

      const { data } = await axios.get('/api/v1/transactions/', {
        params,
        paramsSerializer: params => qs.stringify(params, { arrayFormat: 'repeat' })
      });
      setTransactions(data.data);
      setTotalCount(data.count);

      let totalUsdt = 0, totalEth = 0;
      data.data.forEach(tx => {
        totalUsdt += tx.txn_fee_usdt;
        totalEth += tx.txn_fee_eth;
      });
      setSummary(prev => ({ ...prev, totalUsdt, totalEth }));
    } catch (error) {
      console.error("Error fetching transactions:", error);
    } finally {
      setLoading(false);
    }
  }, [txHashes, startTime, endTime, page, rowsPerPage]);

  const fetchEthPrice = useCallback(async () => {
    try {
      const { data } = await axios.get('/api/v1/prices/ETHUSDT');
      setSummary(prev => ({ ...prev, ethPrice: data.price }));
    } catch (error) {
      console.error("Error fetching ETH price:", error);
    }
  }, []);

  useEffect(() => {
    fetchTransactions();
    fetchEthPrice();
  }, [fetchTransactions, fetchEthPrice, page, rowsPerPage]);

  useEffect(() => {
    const interval = setInterval(fetchEthPrice, 5000);
    return () => clearInterval(interval);
  }, [fetchEthPrice]);

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <Container>
      <Typography variant="h4" gutterBottom>Transaction Fee Tracker</Typography>
      <Box display="flex" flexDirection="column" gap={2} mb={2}>
        <Paper component="form" onBlur={handleTxIdBlur} style={{ padding: '8px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          <TextField
            label="Transaction ID"
            value={txId}
            onChange={handleTxIdChange}
            onKeyPress={handleTxIdKeyPress}
            fullWidth
          />
          {txHashes.map((hash, index) => (
            <Chip
              key={index}
              label={hash}
              onDelete={() => handleDeleteTxHash(hash)}
            />
          ))}
        </Paper>
        <TextField
          label="Start Time (Local)"
          type="datetime-local"
          value={startTime}
          onChange={e => setStartTime(e.target.value)}
          fullWidth
          slotProps={{ input: { readOnly: false }, inputLabel: { shrink: true } }}
        />
        <TextField
          label="End Time (Local)"
          type="datetime-local"
          value={endTime}
          onChange={e => setEndTime(e.target.value)}
          fullWidth
          slotProps={{ input: { readOnly: false }, inputLabel: { shrink: true } }}
        />
        <Button variant="contained" onClick={fetchTransactions} disabled={loading}>
          {loading ? <CircularProgress size={24} /> : "Search"}
        </Button>
      </Box>

      <Typography variant="h6">Summary</Typography>
      <Typography>Total Transaction Fee (USDT): {summary.totalUsdt.toFixed(2)}</Typography>
      <Typography>Total Transaction Fee (ETH): {summary.totalEth.toFixed(6)}</Typography>
      <Typography>Current ETH/USDT Price: {summary.ethPrice.toFixed(2)}</Typography>

      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Transaction Hash</TableCell>
            <TableCell>Timestamp (UTC)</TableCell>
            <TableCell>Txn Fee (USDT)</TableCell>
            <TableCell>Txn Fee (ETH)</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {transactions.map(tx => (
            <TableRow key={tx.tx_hash}>
              <TableCell>{tx.tx_hash}</TableCell>
              <TableCell>{new Date(tx.timestamp).toISOString().replace('T', ' ').replace('Z', '')}</TableCell>
              <TableCell>{tx.txn_fee_usdt.toFixed(2)}</TableCell>
              <TableCell>{tx.txn_fee_eth.toFixed(6)}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <TablePagination
        component="div"
        count={totalCount}
        page={page}
        onPageChange={handlePageChange}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={event => {
          setRowsPerPage(parseInt(event.target.value, 10));
          setPage(0);
        }}
      />
    </Container>
  );
};

export default TransactionTracker;
