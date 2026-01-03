import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material'
import { Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material'
import api from '../services/api'
import { format } from 'date-fns'

export default function Transfers() {
  const [transfers, setTransfers] = useState([])
  const [bases, setBases] = useState([])
  const [assetTypes, setAssetTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingTransfer, setEditingTransfer] = useState(null)
  const [formData, setFormData] = useState({
    source_base: '',
    destination_base: '',
    asset_type: '',
    quantity: '',
    notes: '',
  })

  useEffect(() => {
    fetchTransfers()
    fetchBases()
    fetchAssetTypes()
  }, [])

  const fetchTransfers = async () => {
    setLoading(true)
    try {
      const response = await api.get('/assets/transfers/')
      setTransfers(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch transfers:', error)
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

  const handleOpenDialog = (transfer = null) => {
    if (transfer) {
      setEditingTransfer(transfer)
      setFormData({
        source_base: transfer.source_base,
        destination_base: transfer.destination_base,
        asset_type: transfer.asset_type,
        quantity: transfer.quantity,
        notes: transfer.notes || '',
      })
    } else {
      setEditingTransfer(null)
      setFormData({
        source_base: '',
        destination_base: '',
        asset_type: '',
        quantity: '',
        notes: '',
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingTransfer(null)
  }

  const handleSubmit = async () => {
    try {
      if (editingTransfer) {
        await api.put(`/assets/transfers/${editingTransfer.id}/`, formData)
      } else {
        await api.post('/assets/transfers/', formData)
      }
      handleCloseDialog()
      fetchTransfers()
    } catch (error) {
      console.error('Failed to save transfer:', error)
      alert('Failed to save transfer: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this transfer?')) {
      try {
        await api.delete(`/assets/transfers/${id}/`)
        fetchTransfers()
      } catch (error) {
        console.error('Failed to delete transfer:', error)
        alert('Failed to delete transfer')
      }
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Transfers</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Transfer
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Source Base</TableCell>
              <TableCell>Destination Base</TableCell>
              <TableCell>Asset Type</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Transfer Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transfers.map((transfer) => (
              <TableRow key={transfer.id}>
                <TableCell>{transfer.source_base_name}</TableCell>
                <TableCell>{transfer.destination_base_name}</TableCell>
                <TableCell>{transfer.asset_type_name}</TableCell>
                <TableCell>{transfer.quantity}</TableCell>
                <TableCell>
                  {new Date(transfer.transfer_date).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleOpenDialog(transfer)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    size="small"
                    onClick={() => handleDelete(transfer.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingTransfer ? 'Edit Transfer' : 'New Transfer'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              select
              label="Source Base"
              value={formData.source_base}
              onChange={(e) =>
                setFormData({ ...formData, source_base: e.target.value })
              }
              fullWidth
              required
            >
              {bases.map((base) => (
                <MenuItem key={base.id} value={base.id}>
                  {base.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Destination Base"
              value={formData.destination_base}
              onChange={(e) =>
                setFormData({ ...formData, destination_base: e.target.value })
              }
              fullWidth
              required
            >
              {bases.map((base) => (
                <MenuItem key={base.id} value={base.id}>
                  {base.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Asset Type"
              value={formData.asset_type}
              onChange={(e) =>
                setFormData({ ...formData, asset_type: e.target.value })
              }
              fullWidth
              required
            >
              {assetTypes.map((type) => (
                <MenuItem key={type.id} value={type.id}>
                  {type.name}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Quantity"
              type="number"
              value={formData.quantity}
              onChange={(e) =>
                setFormData({ ...formData, quantity: e.target.value })
              }
              fullWidth
              required
            />
            <TextField
              label="Notes"
              multiline
              rows={3}
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingTransfer ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}


