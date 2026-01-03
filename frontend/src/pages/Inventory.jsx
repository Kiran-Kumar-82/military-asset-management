import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
} from '@mui/material'
import api from '../services/api'

export default function Inventory() {
  const [inventory, setInventory] = useState([])
  const [bases, setBases] = useState([])
  const [assetTypes, setAssetTypes] = useState([])
  const [filters, setFilters] = useState({
    base_id: '',
    asset_type_id: '',
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchInventory()
    fetchBases()
    fetchAssetTypes()
  }, [filters])

  const fetchInventory = async () => {
    setLoading(true)
    try {
      const params = {
        base_id: filters.base_id || undefined,
        asset_type_id: filters.asset_type_id || undefined,
      }
      const response = await api.get('/assets/inventory/', { params })
      setInventory(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch inventory:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchBases = async () => {
    try {
      const response = await api.get('/assets/bases/')
      setBases(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch bases:', error)
    }
  }

  const fetchAssetTypes = async () => {
    try {
      const response = await api.get('/assets/asset-types/')
      setAssetTypes(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch asset types:', error)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Inventory
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            select
            label="Base"
            value={filters.base_id}
            onChange={(e) =>
              setFilters({ ...filters, base_id: e.target.value })
            }
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All Bases</MenuItem>
            {bases.map((base) => (
              <MenuItem key={base.id} value={base.id}>
                {base.name}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            select
            label="Asset Type"
            value={filters.asset_type_id}
            onChange={(e) =>
              setFilters({ ...filters, asset_type_id: e.target.value })
            }
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All Asset Types</MenuItem>
            {assetTypes.map((type) => (
              <MenuItem key={type.id} value={type.id}>
                {type.name}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      </Paper>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Base</TableCell>
              <TableCell>Asset Type</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Last Updated</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {inventory.map((item) => (
              <TableRow key={item.id}>
                <TableCell>{item.base_name}</TableCell>
                <TableCell>{item.asset_type_name}</TableCell>
                <TableCell>{item.asset_type_category}</TableCell>
                <TableCell>{item.quantity}</TableCell>
                <TableCell>
                  {new Date(item.last_updated).toLocaleString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  )
}


