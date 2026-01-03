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
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import api from '../services/api'
import { format } from 'date-fns'

export default function Expenditures() {
  const [expenditures, setExpenditures] = useState([])
  const [bases, setBases] = useState([])
  const [assetTypes, setAssetTypes] = useState([])
  const [loading, setLoading] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingExpenditure, setEditingExpenditure] = useState(null)
  const [formData, setFormData] = useState({
    base: '',
    asset_type: '',
    quantity: '',
    expenditure_date: new Date(),
    reason: '',
    notes: '',
  })

  useEffect(() => {
    fetchExpenditures()
    fetchBases()
    fetchAssetTypes()
  }, [])

  const fetchExpenditures = async () => {
    setLoading(true)
    try {
      const response = await api.get('/assets/expenditures/')
      setExpenditures(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch expenditures:', error)
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

  const handleOpenDialog = (expenditure = null) => {
    if (expenditure) {
      setEditingExpenditure(expenditure)
      setFormData({
        base: expenditure.base,
        asset_type: expenditure.asset_type,
        quantity: expenditure.quantity,
        expenditure_date: new Date(expenditure.expenditure_date),
        reason: expenditure.reason,
        notes: expenditure.notes || '',
      })
    } else {
      setEditingExpenditure(null)
      setFormData({
        base: '',
        asset_type: '',
        quantity: '',
        expenditure_date: new Date(),
        reason: '',
        notes: '',
      })
    }
    setDialogOpen(true)
  }

  const handleCloseDialog = () => {
    setDialogOpen(false)
    setEditingExpenditure(null)
  }

  const handleSubmit = async () => {
    try {
      const data = {
        ...formData,
        expenditure_date: format(formData.expenditure_date, 'yyyy-MM-dd'),
      }
      if (editingExpenditure) {
        await api.put(`/assets/expenditures/${editingExpenditure.id}/`, data)
      } else {
        await api.post('/assets/expenditures/', data)
      }
      handleCloseDialog()
      fetchExpenditures()
    } catch (error) {
      console.error('Failed to save expenditure:', error)
      alert('Failed to save expenditure: ' + (error.response?.data?.detail || error.message))
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this expenditure?')) {
      try {
        await api.delete(`/assets/expenditures/${id}/`)
        fetchExpenditures()
      } catch (error) {
        console.error('Failed to delete expenditure:', error)
        alert('Failed to delete expenditure')
      }
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4">Expenditures</Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            New Expenditure
          </Button>
        </Box>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Base</TableCell>
                <TableCell>Asset Type</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Expenditure Date</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {expenditures.map((expenditure) => (
                <TableRow key={expenditure.id}>
                  <TableCell>{expenditure.base_name}</TableCell>
                  <TableCell>{expenditure.asset_type_name}</TableCell>
                  <TableCell>{expenditure.quantity}</TableCell>
                  <TableCell>{expenditure.expenditure_date}</TableCell>
                  <TableCell>{expenditure.reason}</TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(expenditure)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(expenditure.id)}
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
            {editingExpenditure ? 'Edit Expenditure' : 'New Expenditure'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <TextField
                select
                label="Base"
                value={formData.base}
                onChange={(e) => setFormData({ ...formData, base: e.target.value })}
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
              <DatePicker
                label="Expenditure Date"
                value={formData.expenditure_date}
                onChange={(date) =>
                  setFormData({ ...formData, expenditure_date: date })
                }
                slotProps={{
                  textField: {
                    fullWidth: true,
                  },
                }}
              />
              <TextField
                label="Reason"
                value={formData.reason}
                onChange={(e) =>
                  setFormData({ ...formData, reason: e.target.value })
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
              {editingExpenditure ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  )
}

